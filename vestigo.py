"""Vestigo main file that can
accept arguments and search targets by
outsourcing to modules
"""
from argparse import ArgumentParser
import json
import requests

def trace(file, info=None):
    """Takes JSON file in specific format
    and pings an API with the 'info' and then
    returns the results
    """

    # Try to open JSON file
    try:
        with open(file, "r", encoding="UTF-8") as api_list_json:
            apis = json.loads(api_list_json.read())

    except FileNotFoundError as api_file_error:
        raise api_file_error from FileNotFoundError(f"The file {file} could not be loaded. "
        "This file provides the API info needed to make requests. "
        "You've probably just misplaced it or moved stuff around. "
        "Please check that the 'mods' folder is in the same directory as vestigo.py"
        )

    # Attempt to make requests from it

    ## Goes through each info source separately
    sources = apis.keys()
    for src in sources:
        pass
        #TODO create JSON template for stuff
        #TODO find a way for it to know based off 'src' how fetch API data
        #TODO fetch api data
        #TODO determine whether it was successful or not
        #TODO deal with all errors



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
    if args.email:
        trace("mods/email.json", args.username)

if __name__ == "__main__":
    main()
