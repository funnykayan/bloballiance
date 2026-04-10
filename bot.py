import discord
from discord.ext import commands
from config import client, guild

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree  # commands.Bot has its own CommandTree

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    if bot.get_guild(guild.id) is None:
        print("Guild not found")
        return

    channel = bot.get_guild(guild.id).get_channel(1409606272944177293)
    if channel is None:
        print("Channel not found")
        return

    await tree.sync(guild=discord.Object(id=guild.id))

    await channel.send("I'm here to annoy you. I send a message everytime I come online.")

@tree.command(name="blob", description="Blob, you'll see what happens...", guild=discord.Object(id=guild.id))
async def blob(interaction: discord.Interaction):
    await interaction.response.send_message("Hi :)")

@tree.command(name="hello", description="Hello, mine turtle!", guild=discord.Object(id=guild.id))
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("https://klipy.com/gifs/look-this-dude-he-dumb")


bot.run(client.token)