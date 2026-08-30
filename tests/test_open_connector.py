from unittest.mock import MagicMock
from skills.open_connector_skill import OpenConnectorSkill


def make_response(status=200, payload=None):
    response = MagicMock()
    response.ok = status < 400
    response.status_code = status
    response.json.return_value = payload or {"success": True, "data": {}}
    return response


def test_health_calls_runtime():
    session = MagicMock()
    session.request.return_value = make_response(payload={"success": True})
    result = OpenConnectorSkill(session=session).execute({"action": "health"})
    assert '"success": true' in result.lower()
    assert session.request.call_args.args[:2] == ("GET", "http://localhost:3000/v1/health")


def test_execute_requires_confirmation_for_write_like_action():
    session = MagicMock()
    result = OpenConnectorSkill(session=session).execute({
        "action": "execute",
        "action_id": "gmail.send_email",
        "input": {"to": "x@example.com"},
    })
    assert result.startswith("OPEN_CONNECTOR_APPROVAL_REQUIRED")
    session.request.assert_not_called()


def test_execute_allows_confirmed_action():
    session = MagicMock()
    session.request.return_value = make_response(payload={"success": True, "data": {"sent": True}})
    result = OpenConnectorSkill(session=session).execute({
        "action": "execute",
        "action_id": "github.create_issue",
        "input": {"title": "Test"},
        "confirm": True,
    })
    assert '"sent": true' in result.lower()


def test_missing_runtime_is_reported():
    session = MagicMock()
    session.request.side_effect = __import__("requests").exceptions.ConnectionError()
    result = OpenConnectorSkill(session=session).execute({"action": "health"})
    assert "not reachable" in result
