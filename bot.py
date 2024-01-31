import discord

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$hello"):
        await message.channel.send("Hello!")


client.run("MTIwMjE2NzAyOTY2NzIwNTE0MQ.GcDc5x.6Eb7cZ7Xln8Qg7P74-twUev7SFm2jxFr6aoljE")


# def main() -> int:
#     return 0


# if __name__ == "__main__":
#     main()
