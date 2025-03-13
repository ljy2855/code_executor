import redis
import subprocess
import json
import os

# Redis 설정
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
QUEUE_NAME = "java_code_queue"

# Redis 연결
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)

print("Java Worker Started")

while True:
    try:
        # Redis에서 작업 가져오기
        task = redis_client.brpop(QUEUE_NAME)
        if not task:
            continue

        _, task_json = task
        task_data = json.loads(task_json)

        task_id = task_data["task_id"]
        code = task_data["code"]
        input_data = task_data["input"]

        # Java 코드 저장
        with open("/app/Main.java", "w") as f:
            f.write(code)

        # Java 코드 컴파일
        compile_result = subprocess.run(["javac", "/app/Main.java"], capture_output=True, text=True)

        if compile_result.returncode != 0:
            redis_client.set(f"result:{task_id}", json.dumps({"error": compile_result.stderr}))
            continue

        # 실행
        run_result = subprocess.run(["java", "-cp", "/app", "Main"], input=input_data, capture_output=True, text=True)

        # 결과 저장
        redis_client.set(f"result:{task_id}", json.dumps({"output": run_result.stdout, "error": run_result.stderr}))

    except Exception as e:
        print(f"Error: {e}")
