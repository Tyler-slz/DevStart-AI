from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from services.gemini_service import analyze_code_with_ai, generate_onboarding_guide
from services.github_service import fetch_repo_context, parse_repo_identifier
from services.security_utils import is_sensitive_path, redact_secrets
from services.semgrep_service import run_static_analysis

router = APIRouter(prefix="/analyze", tags=["Analysis"])


class AnalyzeCodeRequest(BaseModel):
    repo: Optional[str] = Field(
        None,
        description="Optional GitHub repository ('owner/repo' or URL) to fetch and analyze",
    )
    code: Optional[str] = Field(
        None, description="Optional raw source code snippet to analyze directly"
    )
    filename: str = Field(
        "snippet.py", description="Filename for the raw code snippet (used for language detection)"
    )
    files: Optional[Dict[str, str]] = Field(
        None, description="Optional mapping of {file_path: file_content} to analyze"
    )
    selected_files: Optional[List[str]] = Field(
        None, description="Optional list of specific file paths to fetch from the repository"
    )
    max_files: int = Field(8, ge=1, le=20, description="Max files to analyze in one batch")


class AnalyzeRepoRequest(BaseModel):
    repo: str = Field(..., description="GitHub repository ('owner/repo' or full GitHub URL)")
    selected_files: Optional[List[str]] = Field(
        None, description="Optional specific files to analyze in this batch"
    )
    max_files: int = Field(8, ge=1, le=20, description="Manageable batch size for source files")


@router.post("/code")
def analyze_code(
    payload: Optional[AnalyzeCodeRequest] = None,
    x_github_token: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Trigger Semgrep static analysis and Gemini AI analysis on source files or a repository.
    Returns identified issues, explanations, proposed code replacements, and a PR draft.
    """
    if payload is None:
        payload = AnalyzeCodeRequest()

    files_to_analyze: Dict[str, str] = {}
    repo_name = payload.repo or "local-snippet"

    # 1. Collect explicitly provided files or snippet (redacting secrets first)
    if payload.files:
        for path, content in payload.files.items():
            if not is_sensitive_path(path) and content:
                files_to_analyze[path] = redact_secrets(content)

    if payload.code:
        if not is_sensitive_path(payload.filename):
            files_to_analyze[payload.filename] = redact_secrets(payload.code)

    # 2. If a GitHub repository was provided and no inline files were sent, fetch a batch from GitHub
    if not files_to_analyze and payload.repo:
        parsed = parse_repo_identifier(payload.repo)
        if not parsed:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid repository identifier '{payload.repo}'. Expected 'owner/repo'.",
            )
        owner, repo = parsed
        repo_name = f"{owner}/{repo}"
        try:
            ctx = fetch_repo_context(
                owner,
                repo,
                max_files=payload.max_files,
                specific_files=payload.selected_files,
                token=x_github_token,
            )
            files_to_analyze = ctx.get("source_files", {})
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=502, detail=f"Failed to fetch repo files: {exc}") from exc

    if not files_to_analyze:
        raise HTTPException(
            status_code=400,
            detail="Provide 'code', 'files', or a valid GitHub 'repo' ('owner/repo') to analyze.",
        )

    # 3. Run Semgrep static analysis + Gemini AI code suggestions
    static_results = run_static_analysis(files_to_analyze)
    ai_results = analyze_code_with_ai(
        files=files_to_analyze,
        static_analysis=static_results,
        repo_name=repo_name,
    )

    return {
        "status": "ok",
        "repo": repo_name,
        "analyzed_files": list(files_to_analyze.keys()),
        **ai_results,
    }


@router.post("/repo")
def analyze_repository(
    payload: AnalyzeRepoRequest,
    x_github_token: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """
    Full repository understanding & analysis pipeline:
    1. Fetches README, CONTRIBUTING, dependency manifests, and a batch of source files.
    2. Generates a step-by-step developer onboarding checklist.
    3. Runs Semgrep static analysis + Gemini AI code review and PR draft generation.
    """
    parsed = parse_repo_identifier(payload.repo)
    if not parsed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid repository identifier '{payload.repo}'. Expected 'owner/repo'.",
        )
    owner, repo = parsed
    full_name = f"{owner}/{repo}"

    try:
        context = fetch_repo_context(
            owner,
            repo,
            max_files=payload.max_files,
            specific_files=payload.selected_files,
            token=x_github_token,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"GitHub API error: {exc}") from exc

    onboarding = generate_onboarding_guide(context)
    source_files = context.get("source_files", {})
    static_results = run_static_analysis(source_files)
    code_analysis = analyze_code_with_ai(
        files=source_files,
        static_analysis=static_results,
        repo_name=full_name,
    )

    response_payload = {
        "status": "ok",
        "repo": full_name,
        "metadata": context.get("metadata"),
        "onboarding": onboarding,
        "analysis": code_analysis,
        "pr_draft": code_analysis.get("pr_draft"),
    }
    return response_payload


@router.post("/onboarding")
def analyze_onboarding(
    payload: AnalyzeRepoRequest,
    x_github_token: Optional[str] = Header(None),
) -> Dict[str, Any]:
    """Generate a step-by-step project onboarding checklist from README, CONTRIBUTING, and dependencies."""
    parsed = parse_repo_identifier(payload.repo)
    if not parsed:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid repository identifier '{payload.repo}'. Expected 'owner/repo'.",
        )
    owner, repo = parsed
    full_name = f"{owner}/{repo}"

    try:
        context = fetch_repo_context(owner, repo, max_files=4, token=x_github_token)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"GitHub API error: {exc}") from exc

    onboarding = generate_onboarding_guide(context)
    return {
        "status": "ok",
        "repo": full_name,
        "metadata": context.get("metadata"),
        "onboarding": onboarding,
    }
