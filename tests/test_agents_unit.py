# tests/test_agents_unit.py
"""
Pure unit tests for MARS agent nodes.

All external I/O (LLM calls, Tavily searches) is mocked so these tests
run in CI with NO API keys and NO network access.
"""

from unittest.mock import MagicMock, patch

import pytest

# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_llm_response(text: str) -> MagicMock:
    """Return a mock that looks like a LangChain AIMessage."""
    mock = MagicMock()
    mock.content = text
    return mock


def _empty_state(**overrides) -> dict:
    base = {
        "main_task": "Test topic",
        "research_findings": [],
        "draft": "",
        "critique_notes": "",
        "revision_number": 0,
        "next_step": "",
        "task_description": "",
        "messages": [],
    }
    base.update(overrides)
    return base


# ── Supervisor tests ──────────────────────────────────────────────────────────

class TestSupervisorNode:
    """Tests for create_supervisor_chain() — uses deterministic logic (no LLM)."""

    def _get_supervisor(self):
        """Import and instantiate supervisor with a mocked LLM."""
        with patch("mars.agents.ChatGroq"), patch("mars.agents.TavilySearch"), patch("mars.agents.load_dotenv"):
            import importlib

            import mars.agents
            importlib.reload(mars.agents)
            return mars.agents.create_supervisor_chain()

    def test_no_research_directs_to_researcher(self):
        supervisor = self._get_supervisor()
        result = supervisor(_empty_state())
        assert result["next_step"] == "researcher"

    def test_approved_critique_directs_to_end(self):
        supervisor = self._get_supervisor()
        state = _empty_state(
            research_findings=["Some findings"],
            draft="A solid draft with content.",
            critique_notes="APPROVED - Excellent report.",
        )
        result = supervisor(state)
        assert result["next_step"] == "END"

    def test_max_revisions_directs_to_end(self):
        supervisor = self._get_supervisor()
        state = _empty_state(
            research_findings=["findings"],
            draft="A draft",
            critique_notes="Needs more detail.",
            revision_number=3,
        )
        result = supervisor(state)
        assert result["next_step"] == "END"

    def test_has_research_no_draft_directs_to_writer(self):
        supervisor = self._get_supervisor()
        state = _empty_state(research_findings=["Found lots of info"])
        result = supervisor(state)
        assert result["next_step"] == "writer"

    def test_critique_feedback_directs_to_writer(self):
        supervisor = self._get_supervisor()
        state = _empty_state(
            research_findings=["findings"],
            draft="Initial draft",
            critique_notes="Needs more depth and citations.",
            revision_number=1,
        )
        result = supervisor(state)
        assert result["next_step"] == "writer"


# ── Writer tests ──────────────────────────────────────────────────────────────

class TestWriterNode:
    """Tests for create_writer_chain() — mocks LLM invoke."""

    def test_writer_returns_string(self):
        with patch("mars.agents.ChatGroq") as mock_groq_cls, \
             patch("mars.agents.TavilySearch"), \
             patch("mars.agents.load_dotenv"):
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = _make_llm_response("# Report\nThis is the draft.")
            mock_groq_cls.return_value = mock_llm

            import importlib

            import mars.agents
            importlib.reload(mars.agents)

            writer = mars.agents.create_writer_chain()
            state = _empty_state(research_findings=["Research point 1"])
            result = writer(state)

        assert isinstance(result, str)
        assert len(result) > 0

    def test_writer_handles_llm_error_gracefully(self):
        with patch("mars.agents.ChatGroq") as mock_groq_cls, \
             patch("mars.agents.TavilySearch"), \
             patch("mars.agents.load_dotenv"):
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = RuntimeError("LLM unavailable")
            mock_groq_cls.return_value = mock_llm

            import importlib

            import mars.agents
            importlib.reload(mars.agents)

            writer = mars.agents.create_writer_chain()
            result = writer(_empty_state())

        assert isinstance(result, str)
        assert "Error" in result or len(result) > 0


# ── Critique tests ────────────────────────────────────────────────────────────

class TestCritiqueNode:
    """Tests for create_critique_chain() — short-circuit logic, no LLM needed."""

    def _get_critique(self):
        with patch("mars.agents.ChatGroq"), patch("mars.agents.TavilySearch"), patch("mars.agents.load_dotenv"):
            import importlib

            import mars.agents
            importlib.reload(mars.agents)
            return mars.agents.create_critique_chain()

    def test_short_draft_auto_approved(self):
        critique = self._get_critique()
        state = _empty_state(draft="Short.")
        result = critique(state)
        assert "APPROVED" in result.upper()

    def test_max_revisions_auto_approved(self):
        critique = self._get_critique()
        state = _empty_state(draft="A" * 200, revision_number=3)
        result = critique(state)
        assert "APPROVED" in result.upper()

    def test_critique_calls_llm_for_normal_draft(self):
        with patch("mars.agents.ChatGroq") as mock_groq_cls, \
             patch("mars.agents.TavilySearch"), \
             patch("mars.agents.load_dotenv"):
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = _make_llm_response("Needs more examples in section 2.")
            mock_groq_cls.return_value = mock_llm

            import importlib

            import mars.agents
            importlib.reload(mars.agents)

            critique = mars.agents.create_critique_chain()
            state = _empty_state(draft="A" * 200, revision_number=1)
            result = critique(state)

        assert isinstance(result, str)
        assert len(result) > 0


# ── _call_llm helper tests ────────────────────────────────────────────────────

class TestCallLLMHelper:
    """Tests for the _call_llm compatibility shim."""

    def _get_call_llm(self):
        with patch("mars.agents.ChatGroq"), patch("mars.agents.TavilySearch"), patch("mars.agents.load_dotenv"):
            import importlib

            import mars.agents
            importlib.reload(mars.agents)
            return mars.agents._call_llm

    def test_prefers_invoke(self):
        call_llm = self._get_call_llm()

        class FakeLLM:
            def invoke(self, x):
                return "invoked:" + x

        assert call_llm(FakeLLM(), "hello") == "invoked:hello"

    def test_falls_back_to_run(self):
        call_llm = self._get_call_llm()

        class FakeLLM:
            def run(self, x):
                return "ran:" + x

        assert call_llm(FakeLLM(), "hello") == "ran:hello"

    def test_falls_back_to_callable(self):
        call_llm = self._get_call_llm()
        assert call_llm(lambda x: "called:" + x, "hello") == "called:hello"

    def test_raises_on_non_callable(self):
        call_llm = self._get_call_llm()
        with pytest.raises(AttributeError):
            call_llm(42, "hello")
