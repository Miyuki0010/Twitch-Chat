import asyncio
import json
import random

import twitchio

# Load bot config from json file
with open('config.json', 'r') as f:
    bot_config = json.load(f)

# Extract config params
BOT_USERNAME = bot_config['bot_username']
OAUTH_TOKEN = bot_config['oauth_token']
CHANNEL_NAME = bot_config['channel_name']
BOT_PREFIX = bot_config['bot_prefix']
timer_minutes = bot_config['initial_timer']['minutes']
timer_seconds = bot_config['initial_timer']['seconds']

# Initialization bot
bot = twitchio.Client(
    token=OAUTH_TOKEN
)

# Join the initial channel
bot.loop.run_until_complete(
    bot.join_channels(
        [CHANNEL_NAME]
    )
)

# Initialization of counter and timer
counter = 0
timer = None
is_paused = False

# Initialization of followers + influence on timer
followers = set()
follower_influence = 0


# Define func to update and start run_timer
async def on_subscribe(subscriber, channel):
    global counter, timer, follower_influence

    # Increase counter and add subs to followers set
    counter += 1
    followers.add(subscriber.name)

    # If first sub, add their influence to timer
    if counter == 1:
        follower_influence += 5

    # Add random time to the timer
    minutes = random.randint(20, 45) + follower_influence
    seconds = minutes * 60

    # Start timer, if it isn't already running
    if timer is None:
        timer = asyncio.create_task(run_timer())
    else:
        # If timer has already finished, set it to None
        if timer.done():
            timer = None


# Define func to run timer and print remaining time
async def run_timer():
    global counter, timer, is_paused

    while counter > 0:
        if not is_paused:
            minutes = random.randint(20, 45) + follower_influence
            seconds = minutes * 60

            while seconds > 0 and not is_paused:
                hours, seconds = divmod(seconds, 3600)
                minutes, seconds = divmod(seconds, 60)
                remaining_time = seconds + minutes * 60 + hours * 3600
                print(f"{hours:02d}:{minutes:02d}")
                await asyncio.sleep(1)

            counter -= 1

    timer = None


# Define func to toggle the timer
async def pause_resume_timer(ctx):
    global is_paused

    # If the command is used by the channel owner or a mod, toggle the timer
    if ctx.author.is_mod or ctx.author.name.lower() == CHANNEL_NAME.lower():
        is_paused = not is_paused

        # Send message to the chat
        if is_paused:
            await ctx.channel.send("Timer is now paused.")
        else:
            await ctx.channel.send("Timer has resumed.")


# Register on_sub as event handler
async def event_subscribe(subscriber, channel):
    await on_subscribe(subscriber, channel)


# Process messages
async def event_message(ctx):
    global follower_influence, timer

    # If message is from bot or does not have the prefix, it gets ignored
    if ctx.author.name.lower() == BOT_USERNAME.lower() or not ctx.content.startswith(BOT_PREFIX):
        return

    # Parse command
    command, *args = ctx.content.split(' ')

    # If command is !remaining, print time
    if command == f"{BOT_PREFIX}remaining":
        if timer is None:
            await ctx.channel.send("There is no marathon currently running.")
        else:
            remaining_time = await run_timer() if timer is not None else 0
            hours, remaining_time = divmod(remaining_time, 3600)
            minutes, seconds = divmod(remaining_time, 60)
            await ctx.channel.send(f"Remaining time: {hours:02d}:{minutes:02d}")
    elif command == f"{BOT_PREFIX}pause" and (await ctx.get_permissions(ctx.author)).moderator or await is_owner(ctx):
        if timer is None:
            await ctx.channel.send("There is no marathon currently running.")
        else:
            timer.cancel()
            timer = None
            await ctx.channel.send("The marathon has been paused.")
    elif command == f"{BOT_PREFIX}resume" and (await ctx.get_permissions(ctx.author)).moderator or await is_owner(ctx):
        if timer is None:
            await ctx.channel.send("There is no marathon currently running.")
        else:
            timer = asyncio.create_task(run_timer())
            await ctx.channel.send("The marathon has been resumed.")
    else:
        await ctx.channel.send("Invalid command.")

        # Add cooldown to the command
        await ctx.send(f".cooldown {BOT_USERNAME} 5")


# Check if user is a mod or the channel owner
async def is_owner(ctx):
    return await ctx.get_permissions(ctx.author).owner


# Start the bot
bot.run()
