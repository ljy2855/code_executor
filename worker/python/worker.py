import asyncio
import aioredis
import json
import os
import subprocess
import tempfile

# Redis 설정
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_QUEUE = "python_code_queue"  # Python 전용 큐

async def execute_code(task):
    """Python 코드 실행 (subprocess.run 사용, input 지원)"""
    task_id = task["task_id"]
    code = task["code"]
    input_data = task.get("input", "")

    print(f"[Worker] Executing Python task {task_id}")

    try:
        # 임시 파일을 생성하여 코드 저장
        with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as temp_file:
            temp_file.write(code.encode())
            temp_file_path = temp_file.name

        # 실행 (input을 전달하고, 실행 시간 제한을 5초로 설정)
        result = subprocess.run(
            ["python3", temp_file_path],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=5
        )

        # 결과 저장
        return {"output": result.stdout, "error": result.stderr}
    except subprocess.TimeoutExpired:
        return {"output": "", "error": "Execution timed out"}
    except Exception as e:
        return {"output": "", "error": str(e)}
    finally:
        # 실행 후 파일 삭제
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

async def worker():
    """Python 전용 Worker 실행"""
    redis = await aioredis.from_url(f"redis://{REDIS_HOST}")

    while True:
        try:
            task_data = await redis.brpop(REDIS_QUEUE)
            if not task_data:
                continue
            
            _, task_json = task_data
            task = json.loads(task_json)

            result = await execute_code(task)
            await redis.setex(f"result:{task['task_id']}", 60, json.dumps(result))

            print(f"[Worker] Task {task['task_id']} completed")

        except Exception as e:
            print(f"[Worker] Error: {e}")

async def main():
    await worker()

if __name__ == "__main__":
    asyncio.run(main())
