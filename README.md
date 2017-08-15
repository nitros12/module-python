# Analyticord-source/module-python/beta
https://analyticord.solutions/api/version?lib=python
This module also requires:
>Requests

>Threading
## Getting started
To use the Analyticord Python module, download the analyticord.py file, place it in the same directory as your bot and add this line to the top:
```
import analyticord
```
Now you've imported the module, you need to login to Analyticord and start logging information, to do this, use this function
```
analyticord.init(token)
```
## Options
Unlike the NodeJS module, you need to edit analyticord.py to provide options, they are all at the top.
```
noMessages (Bool)
```
Don't send any non-error messages.
```
checkForUpdates (Bool)
```
Check for updates at init
```
verifiedMessages (Bool)
```
Enabling this option will return the verified message after data has been sent, that URL will look like this:
```
[AC] Message sent to server, verify it's contents at https://analyticord.solutions/api/verified?id=xxxx-xxxx-xxxx-xxxx
```
Copy this into your browser and make sure the data Analyticord recieved is how you intended it to be, if you need help contact us
https://anlyti.co/discord

## Sending data to Analyticord

To send data like guildJoin, use analyticord.send(), for exmaple
```
analyticord.send('guildJoin', 'verified')
```
This will add a number to the amount of guilds and growth on the Analyticord frontend.

If you would like to log how many messages go through your bot, in your on_message event, add this code:
```
analyticord.message()
```
Every minute the amount of messsages since the last submission will be sent, please do not send the amount of messages yourself as soon as you recieve them, you will be ratelimited & banned, let our program handle it for you.

You can see a list of eventTypes at https://anlyti.co/eventTypes.
