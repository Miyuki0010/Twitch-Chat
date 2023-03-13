import random
import asyncio
import twitchio
import json

# Load bot config from json file
with open('config.json', 'r') as f:
    bot_config = json.load(f)

# Extreact config params
BOT_USERNAME = bot_config['bot_username']
OAUTH_TOKEN = bot_config['oauth_token']
CHANNEL_NAME = bot_config['channel_name']

# intialziaton bot
bot = twitchio.Client(
    token=OAUTH_TOKEN
)

# join the initial channel
bot.loop.run_until_complete(
    bot.join_channels(
        [CHANNEL_NAME]
    )
)


# intialziaton of counter and timer
counter = 0
timer = None


# Define func to update and start run_timer
async def on_subscribe(subscriber, channel):

    global counter, timer
    counter += 1
    if timer is None:
        timer = asyncio.create_task(run_timer())


# Define func to run timer print remainding 18:15
async def run_timer():
    global counter, timer
    while counter > 0:
        minutes = random.randint(20, 45)
        seconds = minutes * 60
        while seconds > 0:
            minutes, seconds = divmod(seconds, 60)
            print(f"{minutes:02d}:{seconds:02d}")
            await asyncio.sleep(1)
        counter -= 1
    timer = None


# Register on_sub as event handler
async def event_subscribe(subscriber, channel):
    await on_subscribe(subscriber, channel)


# Start the bot
bot.run()
