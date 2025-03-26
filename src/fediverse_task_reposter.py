import json

class FediverseTaskReposter:
    """Posts processed task results back to the Fediverse."""

    def send_result(self, result):
        if result.get("remaining_tasks"):
            new_task_post = json.dumps({
                "tasks": result["remaining_tasks"],
                "value": result["result"],
                "options": {},
                "status": "partial"
            })
            print(f"Reposting remaining tasks to Mastodon: {new_task_post}")
        else:
            message = f"@{result['author']} Task completed: {result['original_post']} → {result['result']}"
            print(f"Posting result to Mastodon: {message}")
