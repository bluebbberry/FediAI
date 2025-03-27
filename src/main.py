import json
import logging
import time
import queue
import threading
from fediverse_task_fetcher import FediverseTaskFetcher
from fediverse_task_reposter import FediverseTaskReposter

# Local queues for tasks and results
task_queue = queue.Queue()
result_queue = queue.Queue()


def post_to_queue(task_data):
    """Posts the fetched task to a local queue, including the original post."""
    task_queue.put(task_data)
    print(f"Task enqueued: {task_data}")


def task_worker():
    """Processes tasks from the queue (mock function)."""
    while True:
        task_data = task_queue.get()
        if task_data is None:
            break  # Exit condition for stopping worker threads

        completed_task = task_data["tasks"].pop(0)
        print(f"[Processed {completed_task}]: {task_data['value'].upper()}")
        processed_value = task_data['value'].upper()

        task_result = {
            "author": task_data["author"],
            "result": processed_value,
            "remaining_tasks": task_data["tasks"] if task_data["tasks"] else None
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
            post_to_queue(post)
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
