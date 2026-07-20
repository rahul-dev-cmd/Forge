import re
from fastapi import HTTPException, status
from app.models.enums import RepositoryProvider

# Regular expression checks for Git clone URLs
GITHUB_REGEX = re.compile(
    r"^(https?://github\.com/[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+?(\.git)?|"
    r"git@github\.com:[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+\.git)$"
)

GITLAB_REGEX = re.compile(
    r"^(https?://gitlab\.com/[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+?(\.git)?|"
    r"git@gitlab\.com:[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+\.git)$"
)

BITBUCKET_REGEX = re.compile(
    r"^(https?://bitbucket\.org/[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+?(\.git)?|"
    r"git@bitbucket\.org:[a-zA-Z0-9_\-\.]+/[a-zA-Z0-9_\-\.]+\.git)$"
)

def validate_repo_url(url: str, provider: str) -> None:
    """
    Validate Git clone URL matching specified RepositoryProvider.
    Raises HTTPException (400) if format is invalid.
    """
    if provider == RepositoryProvider.GITHUB.value:
        if not GITHUB_REGEX.match(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GitHub repository URL format. Must match standard HTTPS or SSH git clone layout."
            )
    elif provider == RepositoryProvider.GITLAB.value:
        if not GITLAB_REGEX.match(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid GitLab repository URL format. Must match standard HTTPS or SSH git clone layout."
            )
    elif provider == RepositoryProvider.BITBUCKET.value:
        if not BITBUCKET_REGEX.match(url):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Bitbucket repository URL format. Must match standard HTTPS or SSH git clone layout."
            )
    elif provider == RepositoryProvider.LOCAL.value:
        # Local paths just need to be non-empty strings
        if not url or len(url.strip()) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Local repository path. Cannot be empty."
            )
    # Azure DevOps doesn't have a strict pre-filter here, but it must be non-empty
    elif not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Repository clone URL cannot be empty."
        )
