import json

# Task type to hashtag mapping
task_routing_hashtags = {
    "translation": "fediaitranslation",
    "sentiment_analysis": "fediaisentiment",
    "image_generation": "fediaiimagegen"
}

class FediverseTaskReposter:
    """Posts processed task results back to the Fediverse."""

    def send_result(self, result):
        if result.get("remaining_tasks"):
            next_task = result["remaining_tasks"][0]
            target_hashtag = task_routing_hashtags.get(next_task, "AITask")

            new_task_post = json.dumps({
                "tasks": result["remaining_tasks"],
                "value": result["result"],
                "options": {},
                "status": "partial"
            }) + f" #{target_hashtag}"
            print(f"Reposting remaining tasks to Mastodon: {new_task_post}")
        else:
            message = f"@{result['author']} Task completed: {result['original_post']} → {result['result']}"
            print(f"Posting result to Mastodon: {message}")
