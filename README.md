# discord-bot
The new discord bot for the Competitive Programming Club at Liberty University.

This bot tracks how many points people have gained at Liberty University. It also generates graphs to display people's progress throughout the semester.

## setup
1. Setup the config.json file
2. Make a .env file
3. Put `TOKEN="<TOKEN>"` in the file
4. Replace `<TOKEN>` with your discord bot token

## install
```
pip install -r requirements.txt
```

## running

>! You will need to update the config.json before you begin running the bot to set the correct guildid and leaderboard_channel_id.

to run:
```
python src/main.py
```

made with ❤️ by cameron ([wzid](https://github.com/wzid))