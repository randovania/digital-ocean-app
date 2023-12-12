import json
import logging
import os
import requests

def get_labels(issue):
    return [
        label["name"]
        for label in issue["labels"]
    ]


_channel_for_label = {
    "game: AM2R": "am2r-dev",
    "game: Cave Story": "cave-story-dev",
    "game: Metroid Dread": "dread-dev",
    "game: Metroid Prime 1": "prime-dev",
    "game: Metroid Prime 2 Echoes": "echoes-dev",
    "game: Metroid Prime 3 Corruption": "corruption-dev",
    "game: Metroid: Samus Returns": "samus-returns-dev",
    "game: Super Metroid": "super-metroid-dev",
}

_channel_for_repository = {
    "YAMS": "am2r-dev",
    "py-randomprime": "prime-dev",
    "open-dread-rando": "dread-dev",
    "open-samus-returns-rando": "samus-returns-dev",
    "open-prime-rando": "echoes-dev",
    "Super-Duper-Metroid": "super-metroid-dev",
}

ignored_users = {
    "codecov[bot]",
    "dependabot[bot]",
    "pre-commit-ci[bot]",
}

def _send_to_discord(channel: str, body: dict):
    channel_enviroify = channel.upper().replace("-", "_")
    webhook = os.environ[f"WEBHOOK_{channel_enviroify}"]
    url = f"{webhook}/github"
    r = requests.post(url, json=body)
    r.raise_for_status()
    logging.info("response: %s", str(r))
    return r.text
    

def main(args: dict[str, str]):
    if "repository" not in args:
        return {"body": "unsupported request"}

    if "sender" in args:
        if args["sender"].get("login") in ignored_users:
            return {"body": "ignored user"}

    repository = args["repository"]["name"]

    issue = args.get("issue") or args.get("pull_request")
    if issue:
        if "user" in issue:
            if issue["user"].get("login") in ignored_users:
                return {"body": "ignored user"}

        labels = get_labels(issue)
    else:
        labels = []

    channels = [_channel_for_label.get(label) for label in labels]
    channels = [c for c in channels if c is not None]

    if len(channels) == 1:
        channel_name = channels[0]
    elif repository in _channel_for_repository:
        channel_name = _channel_for_repository[repository]
    else:
        channel_name = "randovania-dev"
    
    result = _send_to_discord(channel_name, args)
    print(result)
    return {"body": result}
