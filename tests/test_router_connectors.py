from agent.router import Router


def test_router_agent_reach():
    result = Router().route("run Agent Reach doctor")
    assert result["tool"] == "agent_reach"
    assert result["arguments"]["action"] == "doctor"


def test_router_open_connector():
    result = Router().route("OpenConnector providers")
    assert result["tool"] == "open_connector"
    assert result["arguments"]["action"] == "providers"
