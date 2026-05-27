"""Code example agent implementation."""

from __future__ import annotations

import base64
from collections.abc import Mapping
import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm_config import LLMProvider, build_chat_model
from labs.agents.labs_post_writer.constants import GITHUB_REPO_URL_PATTERN

from .prompts import LabCodeExamplePrompt
from .schema import LabCodeExampleItem, LabCodeExampleRequest, LabCodeExampleResponse


class LabCodeExampleAgent:
    """Extracts practical code examples from repositories referenced in notes."""

    MAX_FILE_EXCERPT_CHARS = 2500
    MAX_FILES_PER_REPO = 3

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)

    @staticmethod
    def _extract_repositories(text: str) -> list[str]:
        repositories: list[str] = []
        seen: set[str] = set()
        for owner, repo in GITHUB_REPO_URL_PATTERN.findall(text):
            normalized = f"{owner}/{repo.removesuffix('.git')}"
            if normalized not in seen:
                seen.add(normalized)
                repositories.append(normalized)
        return repositories

    @staticmethod
    def _http_get_json(url: str) -> dict:
        request = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "labs-code-example-agent",
            },
        )
        with urlopen(request, timeout=10) as response:
            payload = response.read().decode("utf-8")
        return json.loads(payload)

    @staticmethod
    def _decode_repo_file_content(raw_content: str) -> str:
        if not raw_content:
            return ""
        return base64.b64decode(raw_content).decode("utf-8", errors="ignore")

    @staticmethod
    def _is_candidate_source_file(path: str) -> bool:
        lowered = path.lower()
        if lowered.endswith(
            (
                ".py",
                ".ts",
                ".tsx",
                ".js",
                ".jsx",
                ".go",
                ".java",
                ".kt",
                ".rs",
                ".yaml",
                ".yml",
            )
        ):
            pass
        else:
            return False

        keywords = ("main", "app", "router", "route", "service", "handler", "config")
        return any(keyword in lowered for keyword in keywords)

    def _fetch_repo_context(self, repository: str) -> str:
        owner, repo = repository.split("/", maxsplit=1)
        repo_api = f"https://api.github.com/repos/{owner}/{repo}"
        repo_data = self._http_get_json(repo_api)
        default_branch = repo_data.get("default_branch") or "main"

        lines = [
            f"Repository: {repository}",
            f"Description: {repo_data.get('description') or 'N/A'}",
            f"Language: {repo_data.get('language') or 'N/A'}",
            f"Default branch: {default_branch}",
        ]

        try:
            tree_api = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{default_branch}?recursive=1"
            tree_data = self._http_get_json(tree_api)
            tree_items = tree_data.get("tree", [])
        except Exception:
            tree_items = []

        candidate_paths: list[str] = []
        for item in tree_items:
            item_type = str(item.get("type", ""))
            path = str(item.get("path", ""))
            if item_type == "blob" and self._is_candidate_source_file(path):
                candidate_paths.append(path)
            if len(candidate_paths) >= self.MAX_FILES_PER_REPO:
                break

        for path in candidate_paths:
            try:
                content_api = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
                content_data = self._http_get_json(content_api)
                decoded = self._decode_repo_file_content(str(content_data.get("content", "")))
                if not decoded.strip():
                    continue
                excerpt = decoded.strip()[: self.MAX_FILE_EXCERPT_CHARS]
                lines.append(f"File: {path}")
                lines.append(excerpt)
            except Exception:
                self.logger.info("labs_code_example: could not read file %s in %s", path, repository)

        return "\n".join(lines)

    def _format_human_context(
        self,
        request: LabCodeExampleRequest,
        repositories: list[str],
        repo_context_sections: list[str],
    ) -> str:
        repos_text = "\n".join(f"- {repo}" for repo in repositories) or "- none"
        sections_text = "\n\n---\n\n".join(repo_context_sections) or "No repository context available."
        return (
            f"Max examples: {request.max_examples}\n"
            f"Repositories:\n{repos_text}\n\n"
            "Original notes context:\n"
            f"{request.notes_context}\n\n"
            "Fetched repository context:\n"
            f"{sections_text}"
        )

    def extract_examples(self, request: LabCodeExampleRequest) -> LabCodeExampleResponse:
        repositories = list(dict.fromkeys(request.repositories + self._extract_repositories(request.notes_context)))
        if not repositories:
            return LabCodeExampleResponse(
                examples=[],
                summary="No GitHub repositories found in notes context.",
                warnings=["No repositories detected."],
            )

        warnings: list[str] = []
        repo_context_sections: list[str] = []
        for repository in repositories:
            try:
                repo_context_sections.append(self._fetch_repo_context(repository))
            except HTTPError as exc:
                warnings.append(f"Could not fetch {repository} (http={exc.code}).")
            except URLError as exc:
                warnings.append(f"Network error for {repository} ({exc.reason}).")
            except TimeoutError:
                warnings.append(f"Timeout while fetching {repository}.")
            except Exception:
                self.logger.exception("labs_code_example: failed to fetch context for %s", repository)
                warnings.append(f"Unexpected fetch error for {repository}.")

        if not repo_context_sections:
            return LabCodeExampleResponse(
                examples=[],
                summary="Repository context could not be fetched.",
                warnings=warnings or ["No repository context available."],
            )

        messages = [
            SystemMessage(content=LabCodeExamplePrompt.build_system_prompt()),
            HumanMessage(
                content=self._format_human_context(request, repositories, repo_context_sections)
            ),
        ]

        try:
            structured_llm = self.llm.with_structured_output(LabCodeExampleResponse)
            response = structured_llm.invoke(messages)
        except Exception:
            self.logger.exception("labs_code_example: structured output failed")
            return LabCodeExampleResponse(
                examples=[],
                summary="Failed to generate code examples.",
                warnings=warnings + ["Structured generation failed."],
            )

        if isinstance(response, Mapping):
            response_data = dict(response)
        else:
            response_data = {
                "examples": getattr(response, "examples", []),
                "summary": getattr(response, "summary", ""),
                "warnings": getattr(response, "warnings", []),
            }

        try:
            parsed = LabCodeExampleResponse.model_validate(response_data)
        except Exception:
            self.logger.exception("labs_code_example: invalid structured response")
            return LabCodeExampleResponse(
                examples=[],
                summary="Invalid structured response for code examples.",
                warnings=warnings + ["Invalid model output for code examples."],
            )

        combined_warnings = warnings + parsed.warnings
        return LabCodeExampleResponse(
            examples=[LabCodeExampleItem.model_validate(item) for item in parsed.examples],
            summary=parsed.summary,
            warnings=combined_warnings,
        )
