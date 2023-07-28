"""Vestigo main file that can
accept arguments and search targets by
outsourcing to modules
"""
from argparse import ArgumentParser
import json
import sys
import requests


def load_conf(conf_path):
    """Loads config file,
    have created as procedure so can be
    called to update conf at any point
    """
    try:
        with open(conf_path, "r", encoding="UTF-8") as conf_file:
            config = json.loads(conf_file.read())
        return config
    except (FileNotFoundError, ValueError) as err:
        print(err)
        print(err.args)
        sys.exit(0)

#TODO create config
CONFIG = load_conf("config.json")

def trace(file, info):
    """Takes JSON file in specific format
    and pings an API with the 'info' and then
    returns the results
    """
    #TODO log all this

    # Try to open JSON file
    try:
        with open(file, "r", encoding="UTF-8") as api_list_json:
            apis = json.loads(api_list_json.read())

    except (FileNotFoundError, ValueError) as loading_mod_error:
        print(loading_mod_error)
        print(loading_mod_error.args)
        sys.exit(0)

    # Attempt to make requests from it

    ## Goes through each info source separately
    sources = apis.keys()
    for src in sources:
        # The actual configuration for that specific source e.g. dehashed
        src_conf = apis[src]

        # Grab API KEY if necessary
        if src_conf["details"]["requiresAPIKEY"] is True:
            try:
                with open(CONFIG["apikeys"], "r", encoding="UTF-8") as apikeys_file:
                    api_keys = json.loads(apikeys_file.read())
                    # Attempt to find API key of that specific source
                    try:
                        api_key = api_keys[src]
                    except KeyError as err:
                        print(err)
                        print(err.args)
                        sys.exit(0)
            except (FileNotFoundError, ValueError) as err:
                print(err)
                print(err.args)
                sys.exit(0)

        # Grab headers if necessary
        if src_conf["details"]["headers"] is True:
            headers = CONFIG["headers"]
        elif src_conf["details"]["headers"] is False:
            headers = {}

        # Check whether to execute POST or GET request
        if src_conf["details"]["requestType"] == "POST":
            pass
            #TODO be able to deal with POST requests
        elif src_conf["details"]["requestType"] == "GET":
            # Add params to be sent off with request
            params = src_conf["toSend"]

            # Inject 'info' e.g. email into params
            ## Check whether to inject into URL or not
            if src_conf["details"]["nameOfKeyToFormat"] == "url":
                #TODO iterate through multiple usernames and export to log
                src_conf["details"]["url"] = src_conf["details"]["url"].format(info[0])
            else:
                src_conf["details"]["nameOfKeyToFormat"] = src_conf["details"]["nameOfKeyToFormat"].format(info)

            ## Inject api_key into params if necessary
            if src_conf["details"]["requiresAPIKEY"] is True:
                params["api_key"] = api_key

            # Send request off
            try:
                # Send request
                print(src_conf["details"]["url"])
                req = requests.get(src_conf["details"]["url"], params=src_conf["toSend"], headers=headers, timeout=5, allow_redirects=False)

                # Check result
                if src_conf["details"]["errorType"] == "message":
                    if req.text == src_conf["details"]["errorResponse"]:
                        print("failed")
                    else:
                        print("success")
                elif src_conf["details"]["errorType"] == "statusCode":
                    if req.status_code == int(src_conf["details"]["errorResponse"]):
                        #TODO need to handle redirects if they show up on account that status code is of last request NOT first, allow_redirects has temporarily been set to False
                        print("failed")
                    else:
                        print("success")
            except requests.RequestException as err:
                print(err)
                print(err.args)
                sys.exit(0)

def main():
    """Takes arguments and executes
    commands accordingly
    """

    # Parser options
    parser = ArgumentParser()

    parser.add_argument("--email",
    help="Sets target email")

    parser.add_argument("--phone",
    help="Sets target phone number (international format)")

    parser.add_argument("--name",
    help="Sets target name")

    parser.add_argument("--location",
    help="Sets target approximate location (allows excluding of specific geographical areas)")

    parser.add_argument("--username", nargs="+",
    help="Sets target user/ usernames (accepts multiple usernames - separated by spaces)")

    # Actions based on parser options
    args = parser.parse_args()

    ## Go through all email resources
    if args.username:
        trace("mods/usernames.json", args.username)

if __name__ == "__main__":
    main()
