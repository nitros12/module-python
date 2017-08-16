# Analyticord-source/module-python/beta
https://analyticord.solutions/api/version?lib=python
This module also requires:

aiohttp

## Getting started
to use analyticord, install this repo with `pip install -U git+https://github.com/analyticord/module-python`

Then use
```
import analyticord
```

To create the analyticord instance.
```
analytics = analyticord.AnalytiCord(token)  # where token is your analyticord
token
```

To increment the message count, use:
```await analytics.increment_messages()```

However it is also possible to use method `analytics.hook_bot(bot)` to hook the
on_message of a discord.py bot.
This does not effect other on_message events.

By default the bot creates a loop that sends the message count updates every 60
seconds. you can disable this by passing `do_message_loop=False` to the
AnalytiCord constructor

## Options
Copy this into your browser and make sure the data Analyticord recieved is how you intended it to be, if you need help contact us
https://anlyti.co/discord

## Sending data to Analyticord

To send data like guildJoin, use analyticord.send(), for exmaple
```
await analyticord.send('guildJoin', 'verified')
```
This will add a number to the amount of guilds and growth on the Analyticord frontend.

Every minute the amount of messsages since the last submission will be sent, please do not send the amount of messages yourself as soon as you recieve them, you will be ratelimited & banned, let our program handle it for you.

You can see a list of eventTypes at https://anlyti.co/eventTypes.
