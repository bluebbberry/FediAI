class FediverseTaskFetcher:
    """Fetches posts from the Fediverse containing AI task requests."""

    def fetch_posts(self):
        return [
            {
                "author": "@user",
                "content": '{"tasks": ["translation", "sentiment_analysis"], "value": "Hello, world!", "options": {"language": "fr"}}',
                # "content": '{"tasks": ["translation"], "value": "Hello, world!", "options": {"language": "fr"}}',
                "id": "12345"
            }
        ]