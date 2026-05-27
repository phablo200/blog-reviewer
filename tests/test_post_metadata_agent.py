from labs.agents.labs_post_metadata.agent import LabPostMetadataAgent
from labs.agents.labs_post_metadata.schema import LabPostMetadataRequest


class _StructuredLLMStub:
    def __init__(self, payload):
        self.payload = payload

    def invoke(self, _messages):
        return self.payload


class _LLMStub:
    def __init__(self, payload):
        self.payload = payload

    def with_structured_output(self, _schema):
        return _StructuredLLMStub(self.payload)


class _FailingLLMStub:
    def with_structured_output(self, _schema):
        raise RuntimeError("structured output failed")


def test_generate_returns_structured_metadata_from_mapping() -> None:
    agent = LabPostMetadataAgent.__new__(LabPostMetadataAgent)
    agent.llm = _LLMStub(
        {
            "title": "Testando o Fluxo: Um Guia Pratico",
            "date": "2023-10-10",
            "summary": "Uma exploracao pratica dos processos de teste.",
            "tags": ["Carreira", "Meta"],
            "published": True,
        }
    )
    agent.logger = None  # not used in success path

    response = agent.generate(LabPostMetadataRequest(content="# Post"))

    assert response.title == "Testando o Fluxo: Um Guia Pratico"
    assert response.date == "2023-10-10"
    assert response.tags == ["Carreira", "Meta"]
    assert response.published is True


def test_generate_falls_back_to_empty_defaults_on_failure() -> None:
    agent = LabPostMetadataAgent.__new__(LabPostMetadataAgent)
    agent.llm = _FailingLLMStub()

    class _LoggerStub:
        def exception(self, _message):
            return None

    agent.logger = _LoggerStub()

    response = agent.generate(LabPostMetadataRequest(content="# Post"))

    assert response.title == ""
    assert response.date == ""
    assert response.summary == ""
    assert response.tags == []
    assert response.published is True
