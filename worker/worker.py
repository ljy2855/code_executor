import redis
import json
import subprocess
import os
import time

# Redis 연결
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)

def execute_code(code):
    try:
        result = subprocess.run(
            ["python", "-c", code],
            capture_output=True, text=True, timeout=5
        )
        return {"output": result.stdout, "error": result.stderr}
    except Exception as e:
        return {"output": "", "error": str(e)}

while True:
    _, task_data = redis_client.brpop("code_queue")  # Queue에서 실행 요청 받기
    task = json.loads(task_data)
    task_id = task["task_id"]
    code = task["code"]
    
    print(f"Executing task {task_id}")
    result = execute_code(code)
    
    # 실행 결과 저장
    redis_client.set(f"result:{task_id}", json.dumps(result), ex=60)  # 60초 후 삭제
    print(f"Task {task_id} completed")
    
    time.sleep(1)  # 부하 방지
