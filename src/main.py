import json
import time
import queue
import threading

# Local queues for tasks and results
task_queue = queue.Queue()
result_queue = queue.Queue()


class FediverseTaskFetcher:
    """Fetches posts from the Fediverse containing AI task requests."""

    def fetch_posts(self):
        return [
            {
                "author": "@user",
                "content": '{"tasks": ["translation"], "value": "Hello, world!", "options": {"language": "fr"}}',
                "id": "12345"
            }
        ]


class FediverseTaskReposter:
    """Posts processed task results back to the Fediverse."""

    def send_result(self, result):
        message = f"{result['author']} Task completed: {result['original_post']} → {result['result']}"
        print(f"Posting result to Mastodon: \"{message}\"")


def post_to_queue(task_data, original_post):
    """Posts the fetched task to a local queue, including the original post."""
    task_data["original_post"] = original_post
    task_queue.put(task_data)
    print(f"Task enqueued: {task_data}")


def task_worker():
    """Processes tasks from the queue (mock function)."""
    while True:
        task_data = task_queue.get()
        if task_data is None:
            break  # Exit condition for stopping worker threads

        # Mock processing
        task_result = {
            "author": task_data["author"],
            "original_post": task_data["original_post"],
            "result": f"[Processed]: {task_data['value'].upper()}"
        }

        result_queue.put(task_result)
        print(f"Task processed: {task_result}")
        task_queue.task_done()


def subscribe_to_topic():
    """Subscribes to a topic and listens for processed results."""
    reposter = FediverseTaskReposter()
    print("Subscribed to topic. Listening for task results...")
    while True:
        result = result_queue.get()
        if result is None:
            break  # Exit condition
        reposter.send_result(result)
        result_queue.task_done()


def main():
    """Main function to fetch posts, enqueue tasks, and start workers."""
    fetcher = FediverseTaskFetcher()
    posts = fetcher.fetch_posts()

    for post in posts:
        try:
            task_data = json.loads(post["content"])
            task_data["author"] = post["author"]
            post_to_queue(task_data, post["content"])
        except json.JSONDecodeError:
            print(f"Skipping invalid task format from {post['author']}")

    # Start worker threads
    workers = []
    for _ in range(2):  # Two task workers
        worker = threading.Thread(target=task_worker, daemon=True)
        worker.start()
        workers.append(worker)

    # Start subscriber thread
    subscriber = threading.Thread(target=subscribe_to_topic, daemon=True)
    subscriber.start()

    # Wait for queues to be processed
    task_queue.join()
    result_queue.join()

    # Stop workers
    for _ in range(2):
        task_queue.put(None)
    for worker in workers:
        worker.join()

    # Stop subscriber
    result_queue.put(None)
    subscriber.join()


if __name__ == "__main__":
    main()
