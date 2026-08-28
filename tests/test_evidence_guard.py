from agent.evidence_guard import EvidenceGuard


def test_python_evidence_prefers_official_source():
    evidence = (
        "SOURCE 1 | relevance_score=100\nTITLE: Python Downloads\nURL: https://www.python.org/downloads/\nSNIPPET: official\n"
        "SOURCE 2 | relevance_score=20\nTITLE: Random Python Blog\nURL: https://example.com/python\nSNIPPET: blog"
    )
    result = EvidenceGuard.filter_web_evidence("latest Python release", evidence)
    assert "python.org" in result
    assert "Random Python Blog" not in result


def test_final_instruction_forbids_model_memory():
    result = EvidenceGuard.final_instruction("latest Python release", "VERIFIED_FACT: Python 3.14.7")
    assert "Never substitute pretrained knowledge" in result
    assert "Python 3.14.7" in result
