# ai_worker.py
import time
import mastodon
import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Connect to Mastodon
mastodon_client = mastodon.Mastodon(
    access_token=os.getenv("ACCESS_TOKEN"),
    api_base_url=os.getenv("MASTODON_BASE_URL")  # change if using other instance
)

HASHTAGS = ["whattocook", "diyideas", "learnai", "promptsharing"]

def listen_and_respond():
    since_id = None

    while True:
        for tag in HASHTAGS:
            posts = mastodon_client.timeline_hashtag(tag, since_id=since_id)
            for post in reversed(posts):
                if post["account"]["bot"] is False:
                    reply_text = f"Hi @{post['account']['acct']}!"
                    mastodon_client.status_post(
                        status=reply_text,
                        in_reply_to_id=post["id"]
                    )
                    print(f"Replied to {post['id']}")
                    since_id = max(since_id or 0, post["id"])
        time.sleep(10)

if __name__ == "__main__":
    listen_and_respond()
