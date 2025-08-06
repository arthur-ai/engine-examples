import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import gitlab


class GitLabPRToolInput(BaseModel):
    """Input for the GitLab PR tool"""
    repository: str = Field(..., description="The repository to fetch PRs from (format: owner/repo)")
    since_date: str = Field(..., description="The date to fetch PRs from (format: YYYY-MM-DD)")


class GitLabPRTool(BaseTool):
    """Tool for fetching merged merge requests from GitLab repositories since a given date."""
    
    name: str = "gitlab_pr_tool"
    description: str = "Fetches all merged merge requests from a GitLab repository since a given date"
    args_schema: Type[BaseModel] = GitLabPRToolInput
    
    def _run(self, repository: str, since_date: str) -> List[Dict[str, Any]]:
        """Fetch merged merge requests since a given date."""
        # Get GitLab token
        gitlab_token = os.getenv('GITLAB_TOKEN')
        if not gitlab_token:
            raise ValueError("GITLAB_TOKEN environment variable is required")
        
        # Get GitLab URL (default to gitlab.com if not specified)
        gitlab_url = os.getenv('GITLAB_URL', 'https://gitlab.com')
        
        # Parse repository
        if '/' not in repository:
            raise ValueError("Repository must be in format 'owner/repo'")
        owner, repo = repository.split('/')
        
        # Parse date
        try:
            since_datetime = datetime.strptime(since_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            raise ValueError("Date must be in format 'YYYY-MM-DD'")
        
        # Initialize GitLab client
        gl = gitlab.Gitlab(url=gitlab_url, private_token=gitlab_token)
        
        try:
            # Get the project
            project = gl.projects.get(f"{owner}/{repo}")
        except gitlab.exceptions.GitlabGetError as e:
            raise ValueError(f"Could not find repository {repository}: {e}")
        
        # Fetch merge requests
        merge_requests = project.mergerequests.list(
            state='merged',
            order_by='updated_at',
            sort='desc',
            per_page=100
        )
        
        # Filter merged MRs since the date
        merged_mrs = []
        for mr in merge_requests:
            if mr.merged_at:
                merged_at = datetime.fromisoformat(mr.merged_at.replace('Z', '+00:00'))
                if merged_at >= since_datetime:
                    merged_mrs.append({
                        'title': mr.title,
                        'body': mr.description or '',
                        'html_url': mr.web_url
                    })
        
        return merged_mrs
