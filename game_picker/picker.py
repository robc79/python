# Picks a random game name from the IGDB.


from config import settings
import urllib3
import json
import random


def fetch_random_name(http, endpoint, max_game_id, client_id, token):
    game_id = random.randint(1, max_game_id)
    complete_url = f"{endpoint}/games"
    body = f"fields name; where id = {game_id};"
    response = http.request(
        "POST",
        complete_url,
        body = body,
        headers = {
            "Authorization": token,
            "client-id": client_id
        })
    decoded_response = bytes.decode(response.data)
    json_content = json.loads(decoded_response)
    game_name = None
    if len(json_content) > 0:
        game_name = json_content[0]["name"]
    return game_name


def acquire_token(http, endpoint, client_id, secret):
    query = f"client_id={client_id}&client_secret={secret}&grant_type=client_credentials"
    complete_url = f"{endpoint}?{query}"
    response = http.request("POST", complete_url)
    decoded_response = bytes.decode(response.data)
    json_content = json.loads(decoded_response)
    return f"{json_content["token_type"]} {json_content["access_token"]}"


def pick_name(http):
    token = acquire_token(
        http,
        settings["igdb"]["token_endpoint"],
        settings["igdb"]["client_id"],
        settings["igdb"]["secret"])
    name = fetch_random_name(
        http,
        settings["igdb"]["api_endpoint"],
        settings["igdb"]["max_game_id"],
        settings["igdb"]["client_id"],
        token)
    return name or "<!> Unable to get a game name."


if __name__ == "__main__":
    random.seed()
    http = urllib3.PoolManager()
    name = pick_name(http)
    print(name)
