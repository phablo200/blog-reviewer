import base64
import json
import logging
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .constants import GITHUB_REPO_URL_PATTERN


def extract_github_repositories(markdown: str) -> list[tuple[str, str]]:
    repositories: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for owner, repo in GITHUB_REPO_URL_PATTERN.findall(markdown):
        normalized = (owner, repo.removesuffix(".git"))
        if normalized not in seen:
            seen.add(normalized)
            repositories.append(normalized)
    return repositories


def http_get_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "mebrain-blog-writer",
        },
    )
    with urlopen(request, timeout=10) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def build_repo_context(owner: str, repo: str, logger: logging.Logger) -> str:
    repo_api = f"https://api.github.com/repos/{owner}/{repo}"
    repo_data = http_get_json(repo_api)

    summary_lines = [
        f"Repository: {owner}/{repo}",
        f"Description: {repo_data.get('description') or 'N/A'}",
        f"Language: {repo_data.get('language') or 'N/A'}",
        (
            "Topics: " + ", ".join(repo_data.get("topics", [])[:10])
            if repo_data.get("topics")
            else "Topics: N/A"
        ),
        f"Default branch: {repo_data.get('default_branch') or 'N/A'}",
    ]

    readme_content = ""
    readme_url = f"https://api.github.com/repos/{owner}/{repo}/readme"
    try:
        readme_data = http_get_json(readme_url)
        encoded_content = readme_data.get("content", "")
        if encoded_content:
            readme_content = base64.b64decode(encoded_content).decode(
                "utf-8", errors="ignore"
            )
    except Exception:
        logger.info("blog_post_writer: could not fetch README for %s/%s", owner, repo)

    if readme_content:
        trimmed_readme = readme_content.strip()[:4000]
        summary_lines.append("README excerpt:")
        summary_lines.append(trimmed_readme)

    return "\n".join(summary_lines)


def enrich_context_with_repositories(context: str, logger: logging.Logger) -> str:
    repositories = extract_github_repositories(context)
    if not repositories:
        return context

    logger.info("blog_post_writer: found %s github repository link(s)", len(repositories))

    repo_sections: list[str] = []
    for owner, repo in repositories:
        try:
            repo_sections.append(build_repo_context(owner, repo, logger))
        except HTTPError as exc:
            logger.warning(
                "blog_post_writer: could not fetch repository context for %s/%s (http=%s)",
                owner,
                repo,
                exc.code,
            )
        except URLError as exc:
            logger.warning(
                "blog_post_writer: network error while fetching repository context for %s/%s (%s)",
                owner,
                repo,
                exc.reason,
            )
        except TimeoutError:
            logger.warning(
                "blog_post_writer: timeout while fetching repository context for %s/%s",
                owner,
                repo,
            )
        except Exception:
            logger.exception(
                "blog_post_writer: failed to fetch repository context for %s/%s",
                owner,
                repo,
            )

    if not repo_sections:
        return context

    extra_context = (
        "\n\n## Repository Context (Fetched from GitHub)\n"
        "Use this information to improve technical accuracy of the post.\n\n"
        + "\n\n---\n\n".join(repo_sections)
    )
    return context + extra_context
