# tests/test_tools.py
"""
Tests for the _call_llm helper and researcher node.

These use unittest.mock.patch to avoid any real API calls.
"""

from unittest.mock import MagicMock, patch


def _reload_agents():
    """Reload agents module with all external calls patched out."""
    import importlib

    import mars.agents
    importlib.reload(mars.agents)
    return mars.agents


# ── _call_llm interface tests ─────────────────────────────────────────────────

def test_call_llm_invoke():
    with patch("mars.agents.ChatGroq"), patch("mars.agents.TavilySearch"), patch("mars.agents.load_dotenv"):
        agents = _reload_agents()

    class Dummy:
        def invoke(self, arg):
            return "invoked" + str(arg)

    assert agents._call_llm(Dummy(), "x") == "invokedx"


def test_call_llm_run():
    with patch("mars.agents.ChatGroq"), patch("mars.agents.TavilySearch"), patch("mars.agents.load_dotenv"):
        agents = _reload_agents()

    class Dummy:
        def run(self, arg):
            return "run" + str(arg)

    assert agents._call_llm(Dummy(), "x") == "runx"


def test_call_llm_callable():
    with patch("mars.agents.ChatGroq"), patch("mars.agents.TavilySearch"), patch("mars.agents.load_dotenv"):
        agents = _reload_agents()

    assert agents._call_llm(lambda x: "call" + str(x), "x") == "callx"


# ── Researcher node test ──────────────────────────────────────────────────────

def test_researcher_with_mocked_tavily_and_llm():
    """Researcher should return a dict with 'output' key using mocked tools."""
    with patch("mars.agents.ChatGroq") as mock_groq_cls, \
         patch("mars.agents.TavilySearch") as mock_tavily_cls, \
         patch("mars.agents.load_dotenv"):

        # Mock Tavily returning search results
        mock_tavily = MagicMock()
        mock_tavily.invoke.return_value = {
            "results": [
                {"title": "Test Article", "url": "http://example.com", "content": "Example content"}
            ]
        }
        mock_tavily_cls.return_value = mock_tavily

        # Mock LLM summarisation
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="• Key finding 1\n• Key finding 2")
        mock_groq_cls.return_value = mock_llm

        agents = _reload_agents()
        researcher = agents.create_researcher_agent()
        out = researcher({"input": "test query"})

    assert "output" in out
    assert isinstance(out["output"], str)
    assert len(out["output"]) > 0
