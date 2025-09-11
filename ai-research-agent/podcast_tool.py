import os
import shutil
import yaml
from pydantic import BaseModel, Field
from podcastfy.client import generate_podcast
from portia import Tool, ToolRunContext


class PodcastContent(BaseModel):
    """Content structure for podcast generation."""

    summary: str = Field(..., description="High-level summary for the podcast")
    details: str = Field(..., description="Detailed content for podcast creation")

class PodcastToolSchema(BaseModel):
    """Input for PodcastTool."""

    summary: str = Field(..., description="The high-level summary for the podcast")
    details: str = Field(..., description="Further details that can be used in creating the podcast")


class PodcastTool(Tool[str]):
    """Create a podcast based on a high-level summary and further details."""

    id: str = "podcast_tool"
    name: str = "Podcast Tool"
    description: str = "Used to create a podcast based on a high-level summary and further details."
    args_schema: type[BaseModel] = PodcastToolSchema
    output_schema: tuple[str, str] = ("str", "The location of the output audio file.")

    def run(self, _: ToolRunContext, summary: str, details: str) -> str:
        """Run the Podcast Tool."""
        config_path = os.path.join(os.path.dirname(__file__), "conversation_config.yaml")
        with open(config_path) as config_file:
            conversation_config = yaml.safe_load(config_file)

        if os.getenv("GOOGLE_API_KEY"):
            llm_model_name = "gemini-1.5-pro-latest"
            api_key_label = "GOOGLE_API_KEY"
            tts_model = "google"
            # If your GCP project has had multi-speaker allowlisted, you can use this instead:
            # tts_model = "geminimulti"
        else:
            llm_model_name = "gpt-4o"
            api_key_label = "OPENAI_API_KEY"
            tts_model = "openai"

        audio_file = generate_podcast(
            text=f"A summary of today's AI news is given by: {summary}\n\nDiving deeper, here are the full details: {details}",
            llm_model_name=llm_model_name,
            api_key_label=api_key_label,
            conversation_config=conversation_config,
            tts_model=tts_model,
        )

        # Copy the audio file to a standard location for the latest podcast
        latest_podcast_path = os.path.join(
            os.path.dirname(__file__), "data", "audio", "podcast_latest.mp3"
        )
        
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(latest_podcast_path), exist_ok=True)
        shutil.copy2(audio_file, latest_podcast_path)

        return latest_podcast_path