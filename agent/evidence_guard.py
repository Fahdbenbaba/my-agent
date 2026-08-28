import re
from urllib.parse import urlparse


class EvidenceGuard:
    """Validate and constrain web-search evidence before it reaches the final answer."""

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
        """Keep relevant evidence and strongly prefer primary sources for version questions."""
        q = query.lower()
        if not result:
            return result

        # Python release/version questions are high precision: unrelated ecosystem
        # results must not be presented as evidence.
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
                header = (
                    f"RESEARCH QUERY: {query}\n"
                    "EVIDENCE_GUARD: Only the sources below are admissible evidence. "
                    "For Python release/version questions, prefer python.org/docs.python.org. "
                    "Do not use model memory or unrelated ecosystem projects.\n"
                )
                return header + "\n".join(block for _, block in kept[:3])

        return result

    @staticmethod
    def final_instruction(query: str, evidence: str) -> str:
        return (
            "EVIDENCE GUARD ACTIVE. Answer the user's question using ONLY facts explicitly "
            "supported by the supplied web evidence. Do not add facts from your pretrained "
            "knowledge. Ignore unrelated sources. If the evidence does not establish the "
            "requested fact, say that it could not be verified. For latest/current questions, "
            "do not invent a date or version. Prefer primary-source evidence.\n\n"
            f"USER QUERY: {query}\n\nWEB EVIDENCE:\n{evidence}"
        )
