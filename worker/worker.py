# ai_worker.py
import time
from mastodon import Mastodon
import os
from datetime import datetime, timezone

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Connect to Mastodon
mastodon_client = Mastodon(
    access_token=os.getenv("WORKER_ACCESS_TOKEN"),
    api_base_url=os.getenv("WORKER_MASTODON_BASE_URL")  # change if using other instance
)

target_user_name = os.getenv("USER_NAME")

HASHTAGS = ["whattocook", "diyideas", "learnai", "promptsharing"]

startup_time = datetime.now(timezone.utc)

def listen_and_respond():
    print("Start listening to new prompts ...")

    since_id = None

    while True:
        for tag in HASHTAGS:
            posts = mastodon_client.timeline_hashtag(tag, since_id=since_id)
            for post in reversed(posts):
                username = post['account']['acct']

                if username.lower() == target_user_name.lower():
                    if post["account"]["bot"] is False:
                        post_time = post["created_at"]
                        if post_time < startup_time:
                            continue

                        reply_text = f"What about ordering pizza? @{post['account']['acct']}"
                        mastodon_client.status_post(
                            status=reply_text,
                            in_reply_to_id=post["id"]
                        )
                        print(f"Replied to {post['id']}")
                        if since_id is None:
                            since_id = 0

                        post_id = int(post["id"])
                        since_id = max(int(since_id) if since_id else 0, post_id)
        time.sleep(10)

if __name__ == "__main__":
    listen_and_respond()
