from mastodon_util import MastodonUtil
import json
import re
from html import unescape

class FediverseTaskFetcher:
    """Fetches posts from the Fediverse containing AI task requests."""
    def fetch_posts(self):
        posts = MastodonUtil.fetch_posts()
        if len(posts) == 0:
            print("No posts found for the given hashtag")
        task_posts = []
        for post in posts:
            content = post["content"]
            clean_content = unescape(content)
            clean_content = re.sub(r'<[^>]+>', '', clean_content)  # Remove HTML tags
            clean_content = re.sub(r'#[\w]+', '', clean_content).strip()  # Remove hashtags
            try:
                task_data = json.loads(clean_content)
                task_data["author"] = post["account"]["acct"]
                task_data["id"] = post["id"]
                task_posts.append(task_data)
            except json.JSONDecodeError:
                print(f"JSONDecodeError {clean_content}")
                continue
        return task_posts
        # return [
        #     {
        #         "author": "@user",
        #         "content": '{"tasks": ["translation", "sentiment_analysis"], "value": "Hello, world!", "options": {"language": "fr"}}',
        #         # "content": '{"tasks": ["translation"], "value": "Hello, world!", "options": {"language": "fr"}}',
        #         "id": "12345"
        #     }
        # ]
