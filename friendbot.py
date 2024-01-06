import discord
from discord.ext import commands, tasks
import openai
import time
import asyncio

intents = discord.Intents.all()
intents.presences = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Replace 'YOUR_OPENAI_API_KEY' with your actual OpenAI API key
openai.api_key = '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'

# Custom status messages
status_messages = [
    "Playing a game",
    "Listening to music",
    "Coding",
    "Chatting with users",
]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    update_status.start()

@tasks.loop(minutes=10)  # Change the interval as needed
async def update_status():
    new_status = discord.Game(name=status_messages.pop(0))  # Rotate status messages
    await bot.change_presence(activity=new_status)

@update_status.before_loop
async def before_update_status():
    await bot.wait_until_ready()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if message.content.lower().startswith('!ask'):
        question = message.content[5:].strip()

        typing_indicator = await message.channel.send("FriendBot is thinking...")  # Typing indicator

        start_time = time.time()
        response = await get_chatgpt_response(question)
        end_time = time.time()

        response_time = round(end_time - start_time, 2)

        # Send the response to the Discord channel as an embedded message
        embed = discord.Embed(title="FriendBot's Response", description=response, color=discord.Color.green())
        embed.add_field(name="Response Time", value=f"{response_time} seconds", inline=False)
        await message.channel.send(embed=embed)

        # Delete the typing indicator
        await typing_indicator.delete()

    # Continue with your existing message handling logic

async def get_chatgpt_response(question):
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"Ask me anything: {question}\nAnswer:",
            max_tokens=150
        )
        return response.choices[0].text.strip()

    except Exception as e:
        print(f"Error in get_chatgpt_response: {e}")
        return "Sorry, I encountered an error while processing your request."

@bot.event
async def on_disconnect():
    update_status.cancel()

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
bot.run('MTE5MjMwNjQ0NTc1NzE5NDMzMA.Gtvo1i.J2IZrf1_0nsZ45lVngVfQhU-jhw1LQ9HBGhME4')
