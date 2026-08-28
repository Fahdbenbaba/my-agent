import re
from urllib.parse import urlparse


class EvidenceGuard:
    """Validate web evidence and stop the model from substituting its own facts."""

    PRIMARY_DOMAINS = {
        "python": {"python.org", "docs.python.org"},
    }

    @staticmethod
    def _domain(url: str) -> str:
        try:
            host = urlparse(url).netloc.lower().split(":")[0]
            return host[4:] if host.startswith("www.") else host
        except Exception:
            return ""

    @classmethod
    def filter_web_evidence(cls, query: str, result: str) -> str:
        q = query.lower()
        if not result:
            return result

        if "python" in q and any(k in q for k in ("latest", "current", "release", "version")):
            blocks = re.split(r"(?=SOURCE \d+ \|)", result)
            kept = []
            for block in blocks:
                if not block.strip() or not block.lstrip().startswith("SOURCE"):
                    continue
                url_match = re.search(r"URL:\s*(\S+)", block)
                title_match = re.search(r"TITLE:\s*(.*)", block)
                url = url_match.group(1) if url_match else ""
                title = title_match.group(1).lower() if title_match else ""
                domain = cls._domain(url)
                if domain in cls.PRIMARY_DOMAINS["python"] or "python" in title:
                    kept.append((0 if domain in cls.PRIMARY_DOMAINS["python"] else 1, block))
            kept.sort(key=lambda item: item[0])
            if kept:
                return (
                    f"RESEARCH QUERY: {query}\n"
                    "EVIDENCE_GUARD: Only the sources below are admissible. "
                    "For Python release/version questions, python.org is authoritative. "
                    "Do not use model memory or unrelated ecosystem projects.\n"
                    + "\n".join(block for _, block in kept[:3])
                )
        return result

    @staticmethod
    def final_instruction(query: str, evidence: str) -> str:
        instruction = (
            "EVIDENCE GUARD ACTIVE. Use ONLY facts explicitly supported by WEB EVIDENCE. "
            "Never substitute pretrained knowledge. Never invent dates or versions. "
            "Ignore unrelated sources. If a requested fact is not established, say it could not be verified."
        )
        if "python" in query.lower() and any(k in query.lower() for k in ("latest", "current", "release", "version")):
            instruction += " If WEB EVIDENCE contains VERIFIED_FACT, that exact value is authoritative and MUST be used."
        return instruction + f"\n\nUSER QUERY: {query}\n\nWEB EVIDENCE:\n{evidence}"
