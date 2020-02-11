import sys
import os
import json
import time
import requests
from bs4 import BeautifulSoup

from typing import List, Dict, Any


def load_config() -> Dict[str, str]:
    config: Dict[str, str] = json.loads(open("./config.json", "r").read())
    
    require_keys: List[str] = ["url", "savedir", "session"]
    for require_key in require_keys:
        if require_key not in config.keys():
            print(f"⚠️  Key {require_key} is missing.")
            sys.exit(1)

    return config


def load_challenge_ids(config: Dict[str, str]) -> List[int]:
    response: requests.models.Response = requests.get(url="{}/api/v1/challenges".format(config["url"]), 
                                                      cookies={"session": config["session"]})

    if response.status_code != requests.codes.ok:
        print("⚠️  Failed to fetch challenges.")
        sys.exit(1)

    raw_challenges: List[Dict[str, Any]] = json.loads(response.text)["data"]
    challenge_ids: List[int] = []

    for raw_challenge in raw_challenges:
        challenge_ids.append(raw_challenge["id"])

    return challenge_ids


def load_challenge_spec(config: Dict[str, str], challenge_id: int) -> Dict[str, Any]:
    response: requests.models.Response = requests.get(url="{}/api/v1/challenges/{}".format(config["url"], challenge_id),
                                                      cookies={"session": config["session"]})

    if response.status_code != requests.codes.ok:
        print("⚠️  Failed to fetch challenges. (challenge id {})".format(challenge_id))
        sys.exit(1)

    raw_challenge_spec: Dict[str, Any] = json.loads(response.text)["data"]

    challenge_spec: Dict[str, Any] = {}
    challenge_spec["id"] = raw_challenge_spec["id"]
    challenge_spec["name"] = raw_challenge_spec["name"].lower().replace(" ", "_")
    challenge_spec["category"] = raw_challenge_spec["category"].lower().replace(" ", "-")
    challenge_spec["file_links"] = raw_challenge_spec["files"]
    challenge_spec["description"] = BeautifulSoup(raw_challenge_spec["description"], "html.parser").get_text()

    return challenge_spec


def create_directory(config: Dict[str, str], challenge_spec: Dict[str, Any]) -> None:
    directory_name: str = f"{config['savedir']}/{challenge_spec['category']}-{challenge_spec['name']}"
    
    try:
        os.mkdir(directory_name)
    except:
        print("⚠️  Failed to create directory.")
        sys.exit(1)

    with open(f"{directory_name}/README.md", "w") as f:
        f.write(challenge_spec["description"])

    if "solver" in config.keys():
        with open(f"{directory_name}/{config['solver']}", "w") as f:
            f.write("")

    if len(challenge_spec["file_links"]) != 0:
        for file_link in challenge_spec["file_links"]:
            filename: str = file_link.split("/")[-1].split("?")[0]
            print("📝  Fetch attach file. ({})".format(filename))

            response: requests.models.Response = requests.get(url=f"{config['url']}{file_link}",
                                                              cookies={"session": config["session"]})

            if response.status_code != requests.codes.ok:
                print("⚠️  Failed to fetch attach file. ({})".format(filename))
            
            with open(f"{directory_name}/{filename}", "wb") as f:
                f.write(response.content)
    
    return


def main() -> None:
    print("🌐  Load config.")
    config: Dict[str, str] = load_config()
    print("👌  Done.")
    print("="*30)


    print("🌐  Fetch challenges.")
    challenge_ids: List[int] = load_challenge_ids(config)
    print("👌  Done. (Loaded {} challenges)".format(len(challenge_ids)))
    print("="*30)


    print("🔍  Fetch challenge specs.")
    challenge_specs: List[Dict[str, Any]] = []
    for challenge_id in challenge_ids:
        print("🌐  Fetch challenge spec (id: {}).".format(challenge_id))
        challenge_spec: Dict[str, Any] = load_challenge_spec(config, challenge_id)
        challenge_specs.append(challenge_spec)

        if config.get("mode") == "moderate":
            time.sleep(1)
            
    print("👌  Done.")
    print("="*30)
    

    print("📦  Create directories.")
    os.mkdir(config["savedir"])
    for challenge_spec in challenge_specs:
        print("📦  Create directory (id: {}).".format(challenge_spec["id"]))
        create_directory(config, challenge_spec)
    print("👌  Done.")
    print("="*30)

    print("👍  dirset ended successfully.")
    

if __name__ == '__main__':
    main()