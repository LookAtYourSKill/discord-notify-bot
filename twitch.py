import json
import time
from datetime import datetime
import requests


with open("data.json", 'r') as data_file:
    data = json.load(data_file)

with open('config.json', 'r') as config_file:
    config = json.load(config_file)


# def get_app_access_token():
#     params = {
#         "client_id": config["client_id"],
#         "client_secret": config["client_secret"],
#         "grant_type": "client_credentials"
#     }

#     response = requests.post("https://id.twitch.tv/oauth2/token", params=params)
#     access_token = response.json()["access_token"]
#     return access_token


# access_token = get_app_access_token()
# print(access_token)


def get_users(login_names):
    params = {
        "login": login_names
    }

    headers = {
        "Authorization": "Bearer {}".format(config["access_token"]),
        "Client-Id": config["client_id"]
    }

    response = requests.get(
        "https://api.twitch.tv/helix/users",
        params=params,
        headers=headers
    )
    return {entry["login"]: entry["id"] for entry in response.json()["data"]}


user_test = get_users(data["watchlist"])
print('User: ', user_test)


def get_profile_image(login_names):
    params = {
        "login": login_names
    }

    headers = {
        "Authorization": "Bearer {}".format(config["access_token"]),
        "Client-Id": config["client_id"]
    }

    response = requests.get(
        "https://api.twitch.tv/helix/users",
        params=params, 
        headers=headers
    )
    return {entry["login"]: entry["profile_image_url"] for entry in response.json()["data"]}


profile_pictures = get_profile_image(data["watchlist"])
print('Profile Pictures: ', profile_pictures)



def get_streams(users):
    params = {
        "user_id": users.values()
    }

    headers = {
        "Authorization": "Bearer {}".format(config["access_token"]),
        "Client-Id": config["client_id"]
    }
    response = requests.get(
        "https://api.twitch.tv/helix/streams", 
        params=params, 
        headers=headers
    )
    return {entry["user_login"]: entry for entry in response.json()["data"]}


users_test = get_users(data["watchlist"])
stream_test = get_streams(users_test)
print('Stream: ', stream_test)


online_users = []


def get_notifications():
    global online_users
    users = get_users(data["watchlist"])
    streams = get_streams(users)

    notifications = []
    for user_name in data["watchlist"]:
        if user_name in streams and user_name not in online_users:
            t = datetime.strptime(streams[user_name]['started_at'], "%Y-%m-%dT%H:%M:%SZ")
            started_at = time.mktime(t.timetuple()) + t.microsecond / 1E6
            print(time.time() - started_at)
            if time.time() - started_at < 180:
                notifications.append(streams[user_name])
                online_users.append(user_name)

    return notifications
