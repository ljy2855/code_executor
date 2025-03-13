from fastapi import FastAPI
from pydantic import BaseModel
import redis
import uuid
import json
import os

app = FastAPI()

# Redis 연결
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
redis_client = redis.Redis(host=REDIS_HOST, port=6379, db=0)

class CodeInput(BaseModel):
    code: str
    language: str = "python" | "java" | "C" | "C++"
    input: str = ""

@app.post("/execute")
def execute_code(code_input: CodeInput):
    task_id = str(uuid.uuid4())  # 실행 요청의 고유 ID
    task_data = {"task_id": task_id, "code": code_input.code, "input": code_input.input}
    
    redis_client.lpush(f"{code_input.language}_code_queue", json.dumps(task_data))  # Queue에 추가
    
    return {"task_id": task_id, "status": "queued"}

@app.get("/result/{task_id}")
def get_result(task_id: str):
    result = redis_client.get(f"result:{task_id}")
    if result:
        return json.loads(result)
    return {"task_id": task_id, "status": "pending"}
