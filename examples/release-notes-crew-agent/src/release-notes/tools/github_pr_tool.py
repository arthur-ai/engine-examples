import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from github import Github  # Changed from octokit to PyGithub


class GitHubPRToolInput(BaseModel):
    """Input for the GitHub PR tool"""
    repository: str = Field(..., description="The repository to fetch PRs from (format: owner/repo)")
    since_date: str = Field(..., description="The date to fetch PRs from (format: YYYY-MM-DD)")


class GitHubPRTool(BaseTool):
    """Tool for fetching merged pull requests from GitHub repositories since a given date."""
    
    name: str = "github_pr_tool"
    description: str = "Fetches all merged pull requests from a GitHub repository since a given date"
    args_schema: Type[BaseModel] = GitHubPRToolInput
    
    def _run(self, repository: str, since_date: str) -> List[Dict[str, Any]]:
        """Fetch merged pull requests since a given date."""
        # Get GitHub token
        github_token = os.getenv('GITHUB_TOKEN')
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is required")
        
        # Parse repository
        if '/' not in repository:
            raise ValueError("Repository must be in format 'owner/repo'")
        owner, repo = repository.split('/')
        
        # Parse date
        try:
            since_datetime = datetime.strptime(since_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            raise ValueError("Date must be in format 'YYYY-MM-DD'")
        
        # Initialize PyGithub client and fetch PRs
        gh = Github(github_token)
        repo_obj = gh.get_repo(f"{owner}/{repo}")
        pulls = repo_obj.get_pulls(state='closed', sort='updated', direction='desc')
        
        # Filter merged PRs since the date
        merged_prs = []
        for pr in pulls:
            if pr.merged_at:
                merged_at = pr.merged_at.replace(tzinfo=timezone.utc)
                if merged_at >= since_datetime:
                    merged_prs.append({
                        'title': pr.title,
                        'body': pr.body or '',
                        'html_url': pr.html_url
                    })
        
        return merged_prs
