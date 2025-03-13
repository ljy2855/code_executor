import asyncio
import redis.asyncio as aioredis
import json
import os
import sys
from executor import Executor
# Redis 설정
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
SUPPORT_LANGUAGES = ["python", "java", "c", "cpp"]

class Worker:
    """Worker 클래스 - Redis에서 작업을 가져와 실행"""

    def __init__(self, language):
        if language not in SUPPORT_LANGUAGES:
            print(f"Unsupported language: {language}")
            sys.exit(1)

        self.language = language
        self.queue_name = f"{language}_code_queue"
        self.executor = Executor(language)

    async def run(self):
        """Worker 실행"""
        redis = await aioredis.from_url(f"redis://{REDIS_HOST}")

        while True:
            try:
                task_data = await redis.brpop(self.queue_name)
                if not task_data:
                    continue

                _, task_json = task_data
                task = json.loads(task_json)

                result = await self.executor.execute(task)
                await redis.setex(f"result:{task['task_id']}", 60, json.dumps(result))

                print(f"[Worker] Task {task['task_id']} completed")

            except Exception as e:
                print(f"[Worker] Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python worker.py <language>")
        sys.exit(1)

    language = sys.argv[1]
    worker = Worker(language)
    asyncio.run(worker.run())