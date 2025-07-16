import os

import discord
from dotenv import load_dotenv

from bot.ask import get_answer

load_dotenv(override=True)
bot = discord.Bot()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond(
        "Hey there! Let me know if you need any help with the Portia SDK."
    )


@bot.slash_command(
    name="ask",
    description="Ask a question to the knowledge bot.",
    guild_ids=[os.getenv("DISCORD_SERVER_ID")],
)
async def ask(ctx: discord.ApplicationContext, question: str):
    await ctx.defer()
    if str(ctx.channel_id) != os.getenv("DISCORD_CHANNEL_ID"):
        await ctx.respond("Sorry, this command can't be used in this channel.")
        return
    response = get_answer(question)
    if response is None:
        await ctx.respond("Sorry, I wasn't able to find an answer.")
        return
    await ctx.respond("Question: " + question)
    # There is a 2000 character limit on Discord messages
    if len(response) > 1500:
        l, r = response[1500:1600].split(" ", maxsplit=1)
        await ctx.respond(response[:1500] + l + "...")
        await ctx.respond("..." + r + response[1600:])
    else:
        await ctx.respond(response)


bot.run(os.getenv("DISCORD_BOT_TOKEN"))  # run the bot with the token
