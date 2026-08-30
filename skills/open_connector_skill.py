import json
import os
import uuid
import requests
from skills.base_skill import BaseSkill


class OpenConnectorSkill(BaseSkill):
    """HTTP bridge to a local or explicitly configured OpenConnector runtime."""

    name = "open_connector"
    description = "Discover providers, inspect connections and OAuth configuration, start OAuth authorization, and execute OpenConnector Actions. Provider credentials stay inside the connector runtime."
    schema = {
        "type": "function",
        "function": {
            "name": "open_connector",
            "description": description,
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {
                        "type": "string",
                        "enum": [
                            "health",
                            "providers",
                            "provider",
                            "connections",
                            "oauth_configs",
                            "oauth_authorize",
                            "list_actions",
                            "search_actions",
                            "get_action",
                            "execute",
                        ],
                    },
                    "service": {"type": "string"},
                    "query": {"type": "string"},
                    "action_id": {"type": "string"},
                    "input": {"type": "object"},
                    "connection_name": {"type": "string"},
                    "client_id": {"type": "string"},
                    "client_secret": {"type": "string"},
                    "requested_scopes": {"type": "array", "items": {"type": "string"}},
                    "confirm": {"type": "boolean", "description": "Required for actions that may cause external side effects."},
                },
                "required": ["action"],
            },
        },
    }

    def __init__(self, base_url=None, token=None, session=None):
        self.base_url = (base_url or os.getenv("OPEN_CONNECTOR_URL", "http://localhost:3000")).rstrip("/")
        self.token = token if token is not None else os.getenv("OPEN_CONNECTOR_TOKEN", "")
        self.session = session or requests.Session()

    def _headers(self, extra=None):
        headers = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if extra:
            headers.update(extra)
        return headers

    @staticmethod
    def _may_have_side_effect(action_id: str) -> bool:
        aid = action_id.lower()
        verbs = ("create", "send", "post", "publish", "update", "delete", "remove", "invite", "write", "upload", "transfer", "pay", "purchase")
        return any(f".{verb}" in aid or f"_{verb}" in aid for verb in verbs)

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        try:
            response = self.session.request(method, url, timeout=30, **kwargs)
            try:
                payload = response.json()
            except ValueError:
                payload = {"raw": response.text[:4000]}
        except requests.exceptions.ConnectionError:
            return None, f"OpenConnector is not reachable at {self.base_url}. Start or configure the runtime first."
        except requests.exceptions.RequestException as exc:
            return None, f"OpenConnector request failed: {exc}"
        return payload, None if response.ok else f"HTTP {response.status_code}"

    @staticmethod
    def _clean_oauth_args(arguments):
        payload = {"service": str(arguments.get("service", "")).strip()}
        connection_name = str(arguments.get("connection_name", "")).strip()
        client_id = str(arguments.get("client_id", "")).strip()
        client_secret = str(arguments.get("client_secret", "")).strip()
        requested_scopes = arguments.get("requested_scopes")
        if connection_name:
            payload["connectionName"] = connection_name
        if client_id:
            payload["clientId"] = client_id
        if client_secret:
            payload["clientSecret"] = client_secret
        if isinstance(requested_scopes, list) and requested_scopes:
            payload["requestedScopes"] = [str(scope).strip() for scope in requested_scopes if str(scope).strip()]
        return payload

    def execute(self, arguments: dict) -> str:
        if not isinstance(arguments, dict):
            return "OpenConnector Error: arguments must be a dictionary."

        action = str(arguments.get("action", "health")).strip().lower()
        allowed = {
            "health", "providers", "provider", "connections", "oauth_configs",
            "oauth_authorize", "list_actions", "search_actions", "get_action", "execute",
        }
        if action not in allowed:
            return f"OpenConnector Error: Unsupported action '{action}'."

        if action == "health":
            payload, error = self._request("GET", "/v1/health", headers=self._headers())
        elif action == "providers":
            payload, error = self._request("GET", "/api/catalog", headers=self._headers())
            if error:
                payload, error = self._request("GET", "/v1/providers", headers=self._headers())
        elif action == "provider":
            service = str(arguments.get("service", "")).strip()
            if not service:
                return "OpenConnector Error: No service provided."
            payload, error = self._request("GET", f"/api/providers/{service}", headers=self._headers())
        elif action == "connections":
            payload, error = self._request("GET", "/api/connections", headers=self._headers())
        elif action == "oauth_configs":
            payload, error = self._request("GET", "/api/oauth/configs", headers=self._headers())
        elif action == "oauth_authorize":
            service = str(arguments.get("service", "")).strip()
            if not service:
                return "OpenConnector Error: No OAuth service provided."
            body = self._clean_oauth_args(arguments)
            payload, error = self._request(
                "POST",
                "/api/oauth/authorizations",
                headers=self._headers({"Content-Type": "application/json"}),
                json=body,
            )
        elif action == "list_actions":
            params = {}
            if arguments.get("service"):
                params["service"] = str(arguments["service"])
            payload, error = self._request("GET", "/v1/actions", headers=self._headers(), params=params)
        elif action == "search_actions":
            query = str(arguments.get("query", "")).strip()
            if not query:
                return "OpenConnector Error: No search query provided."
            payload, error = self._request("GET", "/v1/actions/search", headers=self._headers(), params={"q": query})
        elif action == "get_action":
            action_id = str(arguments.get("action_id", "")).strip()
            if not action_id:
                return "OpenConnector Error: No action_id provided."
            payload, error = self._request("GET", f"/v1/actions/{action_id}", headers=self._headers())
        else:
            action_id = str(arguments.get("action_id", "")).strip()
            if not action_id:
                return "OpenConnector Error: No action_id provided."
            if self._may_have_side_effect(action_id) and not bool(arguments.get("confirm", False)):
                return (
                    "OPEN_CONNECTOR_APPROVAL_REQUIRED\n"
                    f"The action '{action_id}' may change an external service. Review it and rerun with confirm=true."
                )
            body = {"input": arguments.get("input", {})}
            headers = self._headers({"Content-Type": "application/json", "Idempotency-Key": uuid.uuid4().hex})
            connection_name = str(arguments.get("connection_name", "")).strip()
            if connection_name:
                headers["x-oo-connector-alias"] = connection_name
            payload, error = self._request("POST", f"/v1/actions/{action_id}", headers=headers, json=body)

        if payload is None:
            return f"OpenConnector Error: {error}"
        if error:
            return f"OpenConnector Error: {error}\n{json.dumps(payload, ensure_ascii=False)}"
        return json.dumps(payload, ensure_ascii=False, indent=2)
