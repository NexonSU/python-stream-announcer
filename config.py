#!/usr/bin/env python

#loglevel: CRITICAL - 50, ERROR - 40, WARNING - 30, INFO - 20, DEBUG - 10
loglevel = 30
logformat = "%(asctime)s - %(levelname)s - %(message)s"
logdatefmt = "%d.%m.%Y %H:%M:%S"

#telegram
telegram_token = 'example:example' #to get token, create bot via @botfather at telegram https://t.me/BotFather
telegram_chat = '@example' #your telegram channel

#twitch
twitch_client_id = 'example' #to get Client ID, visit https://dev.twitch.tv/docs/authentication#registration
twitch_channelid = 'example' #to get your channel ID, you need to make API call https://api.twitch.tv/kraken/users?login=<twitch_login>
twitch_channelname = 'example' #for link in messages

#youtube
youtube_channelid = 'example' #your youtube channel ID. To get channel ID, just open "Your channel" from user panel dock and copy channel ID from address bar.
youtube_channelname = 'example'
