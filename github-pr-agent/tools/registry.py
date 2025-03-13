"""Registry containing GitHub PR tools."""

from portia import InMemoryToolRegistry
from .get_latest_pr_tool import GetLatestPRTool
from .comment_on_pr_tool import CommentOnPRTool

github_pr_tool_registry = InMemoryToolRegistry.from_local_tools(
    [
        GetLatestPRTool(),
        CommentOnPRTool(),
    ],
)