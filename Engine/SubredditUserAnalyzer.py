# Copyright (c) 2018 by James Merrill, all rights reserved

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Engine import UserHistoryScraper, Session, ConfigureLogging, Post
import argparse
import datetime
import logging


class SubredditUserAnalyzer:
    def __init__(self, subreddit_name, number_of_posts, comment_threshold):
        self.subreddit_name = subreddit_name
        self.number_of_posts = number_of_posts
        self.usernames = set()
        self.subreddit = Session.STATIC_SESSION.get_subreddit(subreddit_name)
        self.user_analyses = {}
        self.comment_threshold = comment_threshold
        self.analyzed_posts = []

    def gather_posts(self):
        limit = self.number_of_posts
        posts_to_return = []
        selected_post_ids = set()

        while len(posts_to_return) != self.number_of_posts:
            posts_to_check = self.subreddit.hot(limit=limit)
            for post in posts_to_check:
                if post.id not in selected_post_ids:
                    if post.num_comments < self.comment_threshold:
                        continue
                    else:
                        posts_to_return.append(Post.Post.from_praw_post(post))
                        selected_post_ids.add(post.id)
            limit *= 2

        return posts_to_return

    def gather_users(self):
        posts = self.gather_posts()
        for post in posts:
            logging.info("Gathering users from {}".format(post.title))

            self.usernames = self.usernames.union(post.commenters)
            self.analyzed_posts.append(post)

    def run_analysis(self, days_to_analyze):
        logging.info("Running analysis on {} users".format(len(self.usernames)))

        for username in self.usernames:
            self.user_analyses[username] = UserHistoryScraper.UserHistoryScraper(username, days_to_analyze)

    def dump_analyzed_users(self, target_directory):
        logging.info("Beginning dump")
        now = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        inner_dir_path = os.path.join(target_directory, "{}_{}".format(self.subreddit_name, now))
        users_dir_path = os.path.join(inner_dir_path, "Users")
        posts_dir_path = os.path.join(inner_dir_path, "Posts")

        os.makedirs(inner_dir_path, exist_ok=True)
        os.makedirs(users_dir_path, exist_ok=True)
        os.makedirs(posts_dir_path, exist_ok=True)

        for user in self.user_analyses.values():
            user.dump(users_dir_path)

        for post in self.analyzed_posts:
            post.dump(posts_dir_path)


if __name__ == "__main__":
    ConfigureLogging.configure_logging()

    logging.info("Running SubredditUserAnalysis.py")

    parser = argparse.ArgumentParser()
    parser.add_argument("--subreddit", required=True, help="The name of the subreddit to run analysis on.")
    parser.add_argument("--posts", type=int, required=True, help="How many submissions to gather users from.")
    parser.add_argument("--target_directory", required=True,
                        help="The target directory to create the dump analysis files in.")
    parser.add_argument("--comment_threshold", default=20, type=int, required=False,
                        help="The number of comments a post must have in order to be used for analysis.")

    duration = parser.add_mutually_exclusive_group(required=True)
    duration.add_argument("--days", type=int, help="Number of days to get user history for.")
    duration.add_argument("--months", type=int, help="Number of months to get user history for.")

    args = parser.parse_args()

    days = 0
    if args.days:
        days = args.days
    elif args.months:
        days = args.months * 30

    analyzer = SubredditUserAnalyzer(args.subreddit, args.posts, args.comment_threshold)
    analyzer.gather_users()
    analyzer.run_analysis(days)
    analyzer.dump_analyzed_users(args.target_directory)
