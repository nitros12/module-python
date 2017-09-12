# Analyticord-source/module-python/beta
https://analyticord.solutions/api/version?lib=python

Documentation is available [here](https://discordanalytics-python.readthedocs.io/en/latest/)

## Getting started
To download analyticord python, install this repo via pip: `pip install -U git+https://github.com/analyticord/module-python`

Then use
```python
import analyticord
```

To create the analyticord instance, simply call the constructor of `analyticord.AnalytiCord` like so:
```python
analytics = analyticord.AnalytiCord(token)  # where token is your analyticord token
```

Then start it up with:
```python
await analytics.start()
```

To increment the message count, use:
```python
await analytics.messages.increment()
```

If you are using discord.py, you can also use `analytics.messages.hook_bot(bot)` to hook the relevant events of the bot. This does not affect events already registered with the bot, for example registering messages will not break any current on_message events -- it does not overwrite registered events.

## Sending data to Analyticord

To send data like guildJoin, use `AnalytiCord.send`. For example:
```
await analytics.send('guildJoin', 'verified')
```
This will add a number to the amount of guilds and growth on the Analyticord frontend.

Every minute, the amount of messsages since the last submission will be sent. Please **do not send the amount of messages yourself as soon as you recieve them**; you will be ratelimited and banned. Let the library handle it for you.

## Events
You can see a list of event types at https://anlyti.co/eventTypes.
