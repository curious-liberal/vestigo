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

CONFIG = load_conf("config.json")

def trace(file, info):
    """Takes JSON file in specific format
    and pings an API with the 'info' and then
    returns the results
    """
    #TODO log all this

    # Try to open JSON file
    def load_json(json_file):
        try:
            with open(json_file, "r", encoding="UTF-8") as json_data:
                return json.loads(json_data.read())
        except (FileNotFoundError, ValueError) as loading_mod_error:
            print(loading_mod_error)
            print(loading_mod_error.args)
            sys.exit(0)

    # Load apis
    apis = load_json(file)

    # Attempt to make requests from it

    ## Goes through each info source separately
    sources = apis.keys()
    for src in sources:
        # If multiple 'infos' e.g. usernames, go through each one separately
        for entity in info:
            print(entity)
            # The actual configuration for that specific source e.g. dehashed
            src_conf = apis[src]

            # Grab API KEY if necessary
            if src_conf["details"]["requiresAPIKEY"] is True:
                # API keys for all sites/ sources
                api_keys = load_json(CONFIG["apikeys"])

                # Attempt to find API key of that specific source
                try:
                    api_key = api_keys[src]
                except KeyError as err:
                    print(err)
                    print(err.args)
                    sys.exit(0)

            # Grab headers if necessary
            if src_conf["details"]["headers"] is True:
                headers = CONFIG["headers"]
            elif src_conf["details"]["headers"] is False:
                headers = {}

            # Set whether to send data as JSON
            if src_conf["details"]["sendAsJSON"] is True:
                headers["Content-Type"] = "application/json"

            # Add to_send to be sent off with request
            to_send = src_conf["toSend"]

            # Inject 'info' e.g. email address into to_send
            ## Check whether to inject into URL or not
            if src_conf["details"]["nameOfKeyToFormat"] == "url":
                src_conf["details"]["url"] = src_conf["details"]["url"].format(entity)
            else:
                src_conf["details"]["nameOfKeyToFormat"] = src_conf["details"]["nameOfKeyToFormat"] \
                    .format(info)  # Format curly braces in JSON string

                ## Inject api_key into to_send if necessary
                if src_conf["details"]["requiresAPIKEY"] is True:
                    to_send["api_key"] = api_key

            # Send request off
            try:
                # Check whether to execute POST or GET request
                if src_conf["details"]["requestType"] == "POST":
                    req = requests.post(src_conf["details"]["url"], data=to_send,
                    headers=headers, timeout=8)
                elif src_conf["details"]["requestType"] == "GET":
                    req = requests.get(src_conf["details"]["url"], params=src_conf["toSend"],
                    headers=headers, timeout=8)

                # Check results
                ## Check if error message is present
                if src_conf["details"]["errorType"] == "message":
                    if req.text == src_conf["details"]["errorResponse"]:
                        print("failed")
                    else:
                        print("success")
                # Check for status code error
                elif src_conf["details"]["errorType"] == "statusCode":
                    # If status code is an error
                    try:
                        # Find first status code if redirected
                        if req.history[0].status_code == int(src_conf["details"]["errorResponse"]):
                            print("failed")
                        else:
                            print("success")
                    except IndexError:
                        # Find first status code if NOT redirected
                        if req.status_code == int(src_conf["details"]["errorResponse"]):
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

    ## Go through all username resources
    if args.username:
        # If not a list, put the username in one as a single element \
        # so it can be iterated through - this is so vertigo can easily \
        # accept multiple usernames :D
        if type(args.username) == list:
            trace("mods/usernames.json", args.username)
        else:
            trace("mods/usernames.json", [args.username])

if __name__ == "__main__":
    main()
