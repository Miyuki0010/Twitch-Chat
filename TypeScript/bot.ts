import fs from 'fs';
import * as path from 'path';
import { ChatClient, PrivateMessage, ChatUser } from 'twitch-chat-client';
import { ApiClient, HelixUser, ClientCredentialsAuthProvider } from 'twitch';

interface BotConfig {
  bot_username: string;
  client_id: string;
  client_secret: string;
  access_token: string;
  channel_name: string;
  bot_prefix: string;
  initial_timer: {
    hours: number;
    minutes: number;
    seconds: number;
  };
}

let botConfig: BotConfig;

async function loadConfig() {
  const filePath = path.join(__dirname, 'config.json');
  const data = await fs.promises.readFile(filePath, 'utf8');
  botConfig = JSON.parse(data) as BotConfig;
}

async function main() {
  await loadConfig();

  const {
    bot_username: BOT_USERNAME,
    client_id: CLIENT_ID,
      client_secret: CLIENT_SECRET,
      access_token: ACCESS_TOKEN,
    channel_name: CHANNEL_NAME,
    bot_prefix: BOT_PREFIX,
    initial_timer: {hours: timer_hours, minutes: timer_minutes, seconds: timer_seconds },
  } = botConfig;

  const timerDuration = timer_hours * 60 * 60 * 1000 + timer_minutes * 60 * 1000 + timer_seconds * 1000;
  const authProvider = new ClientCredentialsAuthProvider(CLIENT_ID, CLIENT_SECRET);  
  const apiClient = new ApiClient({ authProvider: authProvider});
  
  const chatClient = new ChatClient(authProvider);

  let counter = 0;
  let timer: NodeJS.Timeout | null = null;
  let isPaused = false;
  let timerStartTime = 0;

  // const followers = new Set<string>();
  // let followerInfluence = 0;

  chatClient.on('message', async (channel, userstate, message, msg) => {
    if (msg.messageType === 'whisper' || !message.startsWith(BOT_PREFIX)) {
      return;
    }

    const args = message.slice(BOT_PREFIX.length).split(' ');
    const command = args.shift()?.toLowerCase() ?? '';
    const currentUser: ChatUser = msg.userInfo;

    if (command === 'remaining' || command === 'r') {
        if (timer === null) {
          chatClient.say(channel, 'There is no marathon currently running.');
        } else {
          let remainingTime;
          if (isPaused) {
            remainingTime = remainingTimerDuration;
          } else {
            remainingTime = timerDuration - (Date.now() - timerStartTime);
          }
          const hours = Math.floor(remainingTime / 3600000);
          const minutes = Math.floor((remainingTime % 3600000) / 60000);
          const seconds = Math.floor((remainingTime % 60000) / 1000);
          chatClient.say(channel, `Remaining time: ${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`);
        }
      } else if (command === 'pause') {
        if (!currentUser || (!currentUser.isMod && currentUser.userName.toLowerCase() !== CHANNEL_NAME.toLowerCase())) {
          chatClient.say(channel, 'Only the channel owner and mods can pause the timer.');
        } else if (timer === null) {
          chatClient.say(channel, 'There is no marathon currently running.');
        } else {
          clearTimeout(timer);
          timer = null;
          isPaused = true;
          remainingTimerDuration = timerDuration - (Date.now() - timerStartTime);
          chatClient.say(channel, 'Timer paused.');
        }
      } else if (command === 'resume') {
        if (!currentUser || (!currentUser.isMod && currentUser.userName.toLowerCase() !== CHANNEL_NAME.toLowerCase())) {
          chatClient.say(channel, 'Only the channel owner and mods can resume the timer.');
        } else if (timer !== null) {
          chatClient.say(channel, 'The marathon is already running!');
          return;
        } else if (isPaused) {
          timer = setTimeout(() => {
            chatClient.say(channel, `Time's up!`);
            timer = null;
            isPaused = false;
          }, remainingTimerDuration);
          chatClient.say(channel, `Timer resumed. ${Math.floor(remainingTimerDuration / 60000).toString().padStart(2, '0')}:${Math.floor((remainingTimerDuration % 60000) / 1000).toString().padStart(2, '0')} remaining.`);
        } else {
          timer = setTimeout(() => {
            chatClient.say(channel, `Time's up!`);
            timer = null;
          }, timer_minutes * 60 * 1000 + timer_seconds * 1000);
          chatClient.say(channel, `Marathon started! ${timer_minutes.toString().padStart(2, '0')}:${timer_seconds.toString().padStart(2, '0')} remaining.`);
        }
      }
 // Start the client connection
 await chatClient.connect();
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});