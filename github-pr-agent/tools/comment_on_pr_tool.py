"""Tool to comment on a GitHub PR."""

import os
from pydantic import BaseModel, Field
from portia.tool import Tool, ToolRunContext
from github import Github, GithubException


class CommentOnPRToolSchema(BaseModel):
    """Schema defining the inputs for the CommentOnPRTool."""

    repo: str = Field(
        ...,
        description="The repository containing the PR, in the format 'owner/repo'",
    )
    pr_number: int = Field(
        ...,
        description="The PR number to comment on",
    )
    comment: str = Field(
        ...,
        description="The comment text to post on the PR",
    )


class CommentOnPRTool(Tool[dict]):
    """Comments on a GitHub PR."""

    id: str = "comment_on_pr_tool"
    name: str = "Comment on PR Tool"
    description: str = "Comments on a GitHub PR"
    args_schema: type[BaseModel] = CommentOnPRToolSchema
    output_schema: tuple[str, str] = (
        "dict",
        "A dictionary containing information about the comment result",
    )

    def run(self, _: ToolRunContext, repo: str, pr_number: int, comment: str) -> dict:
        """Run the CommentOnPRTool."""
        
        github_token = os.getenv("GITHUB_TOKEN")
        if not github_token:
            raise ValueError("GITHUB_TOKEN environment variable is not set")
        
        g = Github(github_token)
        
        try:
            repository = g.get_repo(repo)
            pr = repository.get_pull(pr_number)
            
            # Create a comment on the PR
            comment_obj = pr.create_issue_comment(comment)
            
            return {
                "success": True,
                "comment_id": comment_obj.id,
                "comment_url": comment_obj.html_url,
                "created_at": comment_obj.created_at.isoformat()
            }
            
        except GithubException as e:
            return {
                "success": False,
                "error": f"GitHub API error: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}"
            }