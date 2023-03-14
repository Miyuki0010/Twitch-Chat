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
BOT_PREFIX = bot_config['bot_prefix']
timer_minutes = bot_config['initial_timer']['minutes']
timer_seconds = bot_config['initial_timer']['seconds']

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


# Initialization of followers + influence on timer
followers = set()
follower_influence = 0


# Get inital set of followers
async def get_inital_followers():
    global followers, follower_influence

    followers.response = await bot.get_chatters(CHANNEL_NAME)
    initial_followers = followers.resonse.all

    # Assign initial influence to followers
    follower_influence = len(initial_followers) * 5

    # Add followers to set
    for follower in initial_followers:
        followers.add(follower)


# Define func to update and start run_timer
async def on_subscribe(subscriber, channel):
    global counter, timer, follower_influence

    # Increase counter and add subscriber to followers set
    counter += 1
    followers.add(subscriber.name)

    # if first sub, add their influence to timer
    if counter == 1:
        follower_influence += 5

    # Add random time to the timer
    minutes = random.randint(20, 45) + follower_influence
    seconds = minutes * 60

   # Start timer, if it isn't already running
    if timer is None:
       timer = asyncio.create_task(run_timer())


# Define func to run timer print remainding time
async def run_timer():
    global counter, timer, marathon_running

    while counter > 0:
        minutes = random.randint(20, 45) + follower_influence
        seconds = minutes * 60

        while counter > 0 and  marathon_running:
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            print(f"{hours:02d}:{minutes:02d}")
            await asyncio.sleep(1)

        counter -= 1

    timer = None


# Register on_sub as event handler
async def event_subscribe(subscriber, channel):
    await on_subscribe(subscriber, channel)


async def event_message(ctx):
    global follower_influence, marathon_running, timer

    # If message is from bot or does not have the prefix, it gets ignored
    if ctx.author.name.lower() == BOT_USERNAME.lower() or not ctx.content.startswith(BOT_PREFIX) :
        return

    # Parse command 
    command, *args = ctx.content.split(' ')


    # Only the channel owner or moderators can pause/resume the marathon
    if ctx.author.name.lower() == CHANNEL_NAME.lower() and (ctx.author.is_mod or ctx.author.is_owner):

        # Pause the marathon
        if command == f"{BOT_PREFIX}pause":
            marathon_running = False
            await ctx.channel.send("The marathon has been paused.")

        # Resume the marathon
        elif command == f"{BOT_PREFIX}resume":
            marathon_running = True
            timer = asyncio.create_task(run_timer())
            await ctx.channel.send("The marathon has been resumed.")


    # If command is !remaining. print time
    if command == f"{BOT_PREFIX}remaining":
        minutes, seconds = divmod(timer._coro.cr_frame.f_locals['seconds'],60)
        await ctx.channel.send(f"Remaining time: {minutes:02d}:{seconds:02d}")
    else:
        await ctx.channel.send("There is no marathon curently running.")

    # Add cooldown to the command
    await bot._ws.send_privmsg(ctx.channel.name, f".cooldown {BOT_USERNAME} 5")


# Start the bot
bot.run()