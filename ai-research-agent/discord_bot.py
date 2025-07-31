import asyncio
import os

import discord
from agent import run_agent
from dotenv import load_dotenv

load_dotenv(override=True)
bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    try:
        # Run the agent in a thread to avoid blocking the event loop
        result = await asyncio.get_event_loop().run_in_executor(None, run_agent)

        # Send Discord message with podcast
        channel_id = int(os.getenv("DISCORD_CHANNEL_ID"))
        channel = bot.get_channel(channel_id)
        podcast_path = os.path.join(
            os.path.dirname(__file__), "data", "audio", "podcast_latest.mp3"
        )
        if channel and os.path.exists(podcast_path):
            file = discord.File(podcast_path, filename="ai_news_podcast.mp3")
            msg = f"Daily AI news update \n\n{result.summary}\n\nAlso available as a podcast below - enjoy!"
            await channel.send(msg, file=file)
        else:
            print(f"Channel with ID {channel_id} not found")
    except Exception as e:
        print(f"Agent failed: {e}")
    finally:
        print("Closing Discord bot...")
        await bot.close()


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
