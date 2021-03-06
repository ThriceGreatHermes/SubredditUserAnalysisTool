# Copyright (c) 2018 by James Merrill, all rights reserved

import json
import os
import argparse

HERE = os.path.dirname(__file__)
CREDS_FILE = os.path.abspath(os.path.join(HERE, "..", "credentials.json"))


class Credentials:
    def __init__(self, client_id=None, client_secret=None, client_username=None, client_password=None, user_agent=None):
        raw = dict()
        if not client_id or not client_secret or not client_username or not client_password or not user_agent:
            with open(CREDS_FILE, 'r') as fp:
                raw = json.load(fp)

        self.id = client_id or raw["client_id"]
        self.secret = client_secret or raw["client_secret"]
        self.username = client_username or raw["client_username"]
        self.password = client_password or raw["client_password"]
        self.user_agent = user_agent or raw["user_agent"]

    def dump_to_file(self):
        out_dict = dict()
        out_dict["client_id"] = self.id
        out_dict["client_secret"] = self.secret
        out_dict["client_username"] = self.username
        out_dict["client_password"] = self.password
        out_dict["user_agent"] = self.user_agent

        with open(CREDS_FILE, 'w') as fp:
            json.dump(out_dict, fp)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", default=None, type=str, help="The Client ID to write to the credentials file.")
    parser.add_argument("--secret", default=None, type=str, help="The client secret to write to the credentials file.")
    parser.add_argument("--username", default=None, type=str, help="The username to write to the credentials file.")
    parser.add_argument("--password", default=None, type=str, help="The password to write to the credentials file.")
    parser.add_argument("--user_agent", default=None, type=str, help="The user-agent to write to the credentials file.")
    args = parser.parse_args()

    creds = Credentials(args.id, args.secret, args.username, args.password, args.user_agent)
    creds.dump_to_file()
