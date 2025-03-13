import requests

url = "http://localhost:8000/execute"
code = "print('Hello, Distributed Python!')"
response = requests.post(url, json={"code": code})

task_id = response.json()["task_id"]
print(f"Task ID: {task_id}")

import time

result_url = f"http://localhost:8000/result/{task_id}"
while True:
    result = requests.get(result_url).json()
    if "output" in result:
        print("Execution Result:", result)
        break
    else:
        print("Waiting for execution...")
        time.sleep(1)
