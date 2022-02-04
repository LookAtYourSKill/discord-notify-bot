import json
from datetime import datetime
import requests

with open("config.json", 'r') as config_file:
    config = json.load(config_file)


# things, to get the access_token for the full access
def get_app_access_token():
    # the parameter to be able to get it
    params = {
        "client_id": config["client_id"],
        "client_secret": config["client_secret"],
        "grant_type": "client_credentials"
    }

    # get a response from twitch
    response = requests.post("https://id.twitch.tv/oauth2/token", params=params)
    # look for the access_token
    access_token = response.json()["access_token"]
    # return it
    return access_token


# here you look through the function and give out the access_token
# access_token = get_app_access_token()
# print(access_token)

# the function, to get the users information
def get_users(login_names):
    params = {
        "login": login_names
    }

    headers = {
        "Authorization": "Bearer {}".format(config["access_token"]),
        "Client-Id": config["client_id"]
    }

    # get a response from twitch
    response = requests.get("https://api.twitch.tv/helix/users", params=params, headers=headers)

    # just to get all the infos about the streamers
    # return response.json()

    # just give out the name and the id from the json
    return {entry["login"]: entry["id"] for entry in response.json()["data"]}

#def get_profile_picture(login_names):
#    params = {
#        "login": login_names
#    }

#    headers = {
#        "Authorization": "Bearer {}".format(config["access_token"]),
#        "Client-Id": config["client_id"]
#    }

    # get a response from twitch
#    response = requests.get("https://api.twitch.tv/helix/users", params=params, headers=headers)

    # just to get all the infos about the streamers
    # return response.json()

    # just give out the name and the id from the json
#    return {entry["profile_image_url"] for entry in response.json()["data"]}


# print out the detailed information
# users = get_users(config["watchlist"])
# print(users)

def get_streams(users):
    params = {
        "user_id": users.values()
    }

    headers = {
        "Authorization": "Bearer {}".format(config["access_token"]),
        "Client-Id": config["client_id"]
    }

    # get information about the stream
    response = requests.get("https://api.twitch.tv/helix/streams", params=params, headers=headers)
    return {entry["user_login"]: entry for entry in response.json()["data"]}


# check if streamer are online or offline and get feedback form twitch
# users = get_users(config["watchlist"])
# streams = get_streams(users)
# print(streams)


online_users = {}


def get_notifications():
    # get the information
    users = get_users(config["watchlist"])
    streams = get_streams(users)

    notifications = []
    # go through the config file and watch which names in the watchlist section
    for user_name in config["watchlist"]:

        # when the user is not in the "online_users" list
        if user_name not in online_users:
            # set the start time of the stream to the time now
            online_users[user_name] = datetime.utcnow()

        # when username not in streams
        if user_name not in streams:
            # then set the parameter to None
            online_users[user_name] = None
        # when username is in streams
        else:
            # get the start time from teh stream and reformat it
            started_at = datetime.strptime(streams[user_name]["started_at"], "%Y-%m-%dT%H:%M:%SZ")
            # check if started time is higher then the time now, or if there is None
            if online_users[user_name] is None or started_at > online_users[user_name]:
                # then append the username with the start time
                notifications.append(streams[user_name])
                # set the start time to the user
                online_users[user_name] = started_at

    return notifications
