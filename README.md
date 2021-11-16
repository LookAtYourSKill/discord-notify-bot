# discord-twitch-notification
A discord bot, which will notificate you if a streamer in your watchlist go life!


**#Watchlist**
```
So yeah nothing much to say.
This bot will notificate you, when a streamer from your watchlist go live.
This watchlist you can handle with commands in textchannels or in the config file (config.json).
```

**#Check Streams**
```
Also you can check streams. The bot will check which streamer is live and will give it back.
You can use check_streams_channel, so the bot will send the check message in a specified channel from the config.json!
Otherwise you can use check_streams_privat, so the bot will send you a privat message with the information.
```

**#config.json file**
```
The config.json file is the file, which handles the whole bot.
There you have to fill in everything the bot need. 
```

**#Access Token**

You can get the token with some code:

```
  import json
  import requests

  with open("config.json", 'r') as config_file:
      config = json.load(config_file)
      
  def get_app_access_token():
      params = {
          "client_id": config["client_id"],
          "client_secret": config["client_secret"],
          "grant_type": "client_credentials"
      }

      response = requests.post("https://id.twitch.tv/oauth2/token", params=params)
      access_token = response.json()["access_token"]
      return access_token

  access_token = get_app_access_token()
  print(access_token)
```
