import discord
import os
from dotenv import load_dotenv

from ask import get_answer

load_dotenv(override=True)  # load all the variables from the env file
bot = discord.Bot()

ASK_QUESTION_CHANNEL_ID = 1341374149678858311  # ask question channel id
PORTIA_GUILD_ID = 1331293596665512067


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey I'm listening!")


@bot.slash_command(
    name="ask",
    description="Ask a question to the knowledge bot. Responses are augmented via the Portia SDK docs.",
    guild_ids=[PORTIA_GUILD_ID],
)
async def ask(ctx: discord.ApplicationContext, question: str):
    await ctx.defer()
    if ctx.channel_id != ASK_QUESTION_CHANNEL_ID:
        await ctx.respond(
            "This command can only be used in the #knowledge-bot channel."
        )
        return
    response = get_answer(question)
    await ctx.respond(response)


bot.run(os.getenv("DISCORD_BOT_TOKEN"))  # run the bot with the token
