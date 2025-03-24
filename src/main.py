from fastapi import FastAPI, HTTPException
import asyncio
import json
import aio_pika
from pydantic import BaseModel
from mastodon import Mastodon

# Configuration (Replace with your own values)
RABBITMQ_URL = "amqp://guest:guest@localhost/"
MASTODON_ACCESS_TOKEN = "your_mastodon_access_token"
MASTODON_API_BASE_URL = "https://mastodon.instance"
HASHTAG = "AITask"
RESULTS_QUEUE = "ai_results"

# Initialize Mastodon API
mastodon = Mastodon(access_token=MASTODON_ACCESS_TOKEN, api_base_url=MASTODON_API_BASE_URL)

# Initialize FastAPI
app = FastAPI(title="FediMQAPI", description="API for posting AI tasks to the Fediverse and FediMQ message queue.")


# Define task request model
class TaskRequest(BaseModel):
    tasks: list[str]
    value: str
    options: dict = {}
    author: str


# Connect to RabbitMQ
async def publish_to_queue(message: dict, routing_key: str):
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(message).encode()),
            routing_key=routing_key
        )


# API endpoint to submit a task
@app.post("/submit-task")
async def submit_task(task: TaskRequest):
    message = {
        "tasks": task.tasks,
        "value": task.value,
        "options": task.options,
        "author": task.author
    }
    await publish_to_queue(message, "ai_tasks")
    return {"message": "Task submitted successfully", "task": message}


# Fetch latest posts with the given hashtag periodically
async def fetch_activitypub_tasks():
    while True:
        print("Fetching new tasks from Mastodon...")
        posts = mastodon.timeline_hashtag(HASHTAG, limit=5)
        for post in posts:
            try:
                content = post["content"].replace("<p>", "").replace("</p>", "")  # Remove HTML tags
                task_data = json.loads(content)
                task_data["author"] = post["account"]["acct"]
                await publish_to_queue(task_data, "ai_tasks")
                print(f"Task received: {task_data}")
            except json.JSONDecodeError:
                print("Skipping invalid task format.")
        await asyncio.sleep(60)  # Fetch new posts every 60 seconds


# Consumer that processes AI tasks
async def consume_tasks():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("ai_tasks")

        async for message in queue:
            async with message.process():
                task = json.loads(message.body)
                print(f"Processing AI task: {task}")

                if task["tasks"]:
                    current_task = task["tasks"].pop(0)
                    response = {
                        "author": task["author"],
                        "result": f"Task '{current_task}' processed for @{task['author']}",
                        "tasks": task["tasks"]
                    }
                    await publish_to_queue(response, RESULTS_QUEUE)
                    print(f"Posted result to results queue: {response}")

                if task["tasks"]:
                    await publish_to_queue(task, "ai_tasks")  # Repost with remaining tasks
                else:
                    print("All tasks completed.")


# Consumer that listens for AI results and posts them to Mastodon
async def consume_results():
    connection = await aio_pika.connect_robust(RABBITMQ_URL)
    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue(RESULTS_QUEUE)

        async for message in queue:
            async with message.process():
                result = json.loads(message.body)
                mastodon.status_post(f"@{result['author']} {result['result']} #{HASHTAG}")
                print(f"Posted result to Mastodon: {result['result']}")


# Background tasks for consuming messages and fetching tasks from Mastodon
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(consume_tasks())
    asyncio.create_task(fetch_activitypub_tasks())
    asyncio.create_task(consume_results())
