from types import SimpleNamespace

from labs.agents.labs_code_example.agent import LabCodeExampleAgent
from labs.agents.labs_code_example.schema import LabCodeExampleRequest


class _StructuredLLMStub:
    def __init__(self, response=None, raises: Exception | None = None):
        self.response = response
        self.raises = raises

    def invoke(self, _messages):
        if self.raises:
            raise self.raises
        return self.response


class _LLMStub:
    def __init__(self, response=None, raises: Exception | None = None):
        self.response = response
        self.raises = raises

    def with_structured_output(self, _schema):
        return _StructuredLLMStub(response=self.response, raises=self.raises)


def test_extract_examples_without_repositories_returns_warning() -> None:
    agent = LabCodeExampleAgent.__new__(LabCodeExampleAgent)
    agent.logger = SimpleNamespace(exception=lambda *args, **kwargs: None)
    agent.llm = _LLMStub(response={})

    response = agent.extract_examples(
        LabCodeExampleRequest(notes_context="No links here", repositories=[])
    )

    assert response.examples == []
    assert "repositories" in response.summary.lower()
    assert response.warnings


def test_extract_examples_successful_structured_response(monkeypatch) -> None:
    agent = LabCodeExampleAgent.__new__(LabCodeExampleAgent)
    agent.logger = SimpleNamespace(exception=lambda *args, **kwargs: None)
    agent.llm = _LLMStub(
        response={
            "examples": [
                {
                    "repository": "octocat/hello-world",
                    "file_path": "app/main.py",
                    "language": "python",
                    "snippet": "def main():\n    return 'ok'",
                    "why_it_matters": "Shows main app flow",
                    "integration_hint": "Use it in architecture section",
                }
            ],
            "summary": "One strong example found.",
            "warnings": [],
        }
    )

    monkeypatch.setattr(
        agent,
        "_fetch_repo_context",
        lambda _repo: "Repository: octocat/hello-world\nFile: app/main.py\ndef main(): pass",
    )

    response = agent.extract_examples(
        LabCodeExampleRequest(
            notes_context="https://github.com/octocat/hello-world", repositories=[]
        )
    )

    assert len(response.examples) == 1
    assert response.examples[0].repository == "octocat/hello-world"
    assert response.summary == "One strong example found."


def test_extract_examples_structured_generation_failure_returns_fallback(monkeypatch) -> None:
    agent = LabCodeExampleAgent.__new__(LabCodeExampleAgent)
    agent.logger = SimpleNamespace(exception=lambda *args, **kwargs: None)
    agent.llm = _LLMStub(raises=RuntimeError("llm failed"))

    monkeypatch.setattr(
        agent,
        "_fetch_repo_context",
        lambda _repo: "Repository: octocat/hello-world\nFile: app/main.py\ndef main(): pass",
    )

    response = agent.extract_examples(
        LabCodeExampleRequest(
            notes_context="https://github.com/octocat/hello-world", repositories=[]
        )
    )

    assert response.examples == []
    assert "Failed to generate" in response.summary
    assert any("Structured generation failed" in warning for warning in response.warnings)
