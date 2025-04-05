import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class MastodonUtil:
    """Handles Mastodon API interactions."""

    @staticmethod
    def fetch_posts():
        MASTODON_BASE_URL = os.getenv("MASTODON_BASE_URL", "https://mastodon.instance/api/v1")
        ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "your_access_token_here")
        hashtag = os.getenv("FETCH_HASHTAG", "AITask")  # Default to #AITask if not set
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
        response = requests.get(
            f"{MASTODON_BASE_URL}/timelines/tag/{hashtag}",
            headers=headers,
            params={"limit": 5}
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Found no post under the given hashtag: {hashtag}")
            return []

    @staticmethod
    def post_status(content):
        MASTODON_BASE_URL = os.getenv("MASTODON_BASE_URL", "https://mastodon.instance/api/v1")
        ACCESS_TOKEN = os.getenv("ACCESS_TOKEN", "your_access_token_here")
        headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
        payload = {"status": content}
        response = requests.post(f"{MASTODON_BASE_URL}/statuses", headers=headers, json=payload)
        if response.status_code == 200:
            print("Successfully posted to Mastodon.")
        else:
            print("Failed to post to Mastodon.", response.text)
