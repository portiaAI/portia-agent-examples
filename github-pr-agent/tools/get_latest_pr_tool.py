"""Tool to get the latest PR from a GitHub repository."""

import os
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
from github import Github, GithubException


class GetLatestPRToolSchema(BaseModel):
    """Schema defining the inputs for the GetLatestPRTool."""

    repo: str = Field(
        ...,
        description="The repository to get the latest PR from, in the format 'owner/repo'",
    )


class GetLatestPRTool(Tool[dict]):
    """Gets the latest PR from a GitHub repository."""

    id: str = "get_latest_pr_tool"
    name: str = "Get Latest PR Tool"
    description: str = "Gets the latest PR from a GitHub repository"
    args_schema: type[BaseModel] = GetLatestPRToolSchema
    output_schema: tuple[str, str] = (
        "dict",
        "A dictionary containing information about the latest PR",
    )

    def run(self, _: ToolRunContext, repo: str) -> dict:
        """Run the GetLatestPRTool."""
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is not set")
        
        g = Github(github_token)
        
        try:
            repository = g.get_repo(repo)
            pulls = repository.get_pulls(state="open", sort="created", direction="desc")
            
            if pulls.totalCount == 0:
                return {"error": "No open PRs found in the repository"}
            
            latest_pr = pulls[0]
            
            # Get the PR files
            files = []
            for file in latest_pr.get_files():
                files.append({
                    "filename": file.filename,
                    "status": file.status,
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch
                })
            
            return {
                "pr_number": latest_pr.number,
                "title": latest_pr.title,
                "body": latest_pr.body,
                "user": latest_pr.user.login,
                "created_at": latest_pr.created_at.isoformat(),
                "updated_at": latest_pr.updated_at.isoformat(),
                "html_url": latest_pr.html_url,
                "files": files
            }
            
        except GithubException as e:
            return {"error": f"GitHub API error: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}