import os
import subprocess
import tempfile
from typing import Dict


class Task:
    """실행할 코드와 입력 데이터를 저장하는 Task 클래스"""

    def __init__(self, id: str, code: str, input: str = ""):
        self.id = id
        self.code = code
        self.input = input or ""  # ✅ None 방지 처리


class Executor:
    """각 언어별 코드 실행기"""

    def __init__(self, language: str):
        self.language = language

    async def execute(self, task_dict: Dict) -> Dict[str, str]:
        """언어별 실행 함수 매핑"""
        execute_methods = {
            "python": self._execute_python,
            "java": self._execute_java,
            "c": self._execute_c,
            "cpp": self._execute_cpp,
        }
        task = Task(
            id=task_dict["task_id"],
            code=task_dict["code"],
            input=task_dict.get("input", "") 
        )

        if self.language in execute_methods:
            return await execute_methods[self.language](task)
        return {"output": "", "error": f"Unsupported language: {self.language}"}

    async def _execute_python(self, task: Task):
        """Python 코드 실행"""
        return await self._execute_code(task, "python3", ".py")

    async def _execute_java(self, task: Task):
        """Java 코드 실행"""
        task_id = task.id
        code = task.code
        input_data = task.input

        print(f"[Worker] Executing Java task {task_id}")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                java_file_path = os.path.join(temp_dir, "Main.java")

                # Java 코드 저장
                with open(java_file_path, "w") as f:
                    f.write(code)

                # Java 코드 컴파일
                compile_result = subprocess.run(["javac", java_file_path], capture_output=True, text=True)
                if compile_result.returncode != 0:
                    return {"output": "", "error": compile_result.stderr}

                run_result = subprocess.run(
                    ["java", "-cp", temp_dir, "Main"],
                    input=input_data, capture_output=True, text=True, timeout=5
                )

                return {"output": run_result.stdout, "error": run_result.stderr}

        except subprocess.TimeoutExpired:
            return {"output": "", "error": "Execution timed out (possible infinite loop)"}
        except Exception as e:
            return {"output": "", "error": str(e)}

    async def _execute_c(self, task: Task):
        """C 코드 실행"""
        return await self._execute_compiled(task, "gcc", ".c")

    async def _execute_cpp(self, task: Task):
        """C++ 코드 실행"""
        return await self._execute_compiled(task, "g++", ".cpp")

    async def _execute_code(self, task: Task, interpreter: str, extension: str):
        """스크립트 언어 (Python) 실행"""
        task_id = task.id
        code = task.code
        input_data = task.input

        print(f"[Worker] Executing {self.language} task {task_id}")

        try:
            with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
                temp_file.write(code.encode())
                temp_file_path = temp_file.name

            # 실행 (입력값 전달, 실행 시간 제한 5초 설정)
            result = subprocess.run(
                [interpreter, temp_file_path],
                input=input_data, text=True, capture_output=True, timeout=5
            )

            return {"output": result.stdout, "error": result.stderr}

        except subprocess.TimeoutExpired:
            return {"output": "", "error": "Execution timed out"}
        except Exception as e:
            return {"output": "", "error": str(e)}
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

    async def _execute_compiled(self, task: Task, compiler: str, extension: str):
        """컴파일 언어 (C, C++) 실행"""
        task_id = task.id
        code = task.code
        input_data = task.input

        print(f"[Worker] Executing {self.language} task {task_id}")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                source_file_path = os.path.join(temp_dir, f"main{extension}")
                binary_path = os.path.join(temp_dir, "a.out")

                # 소스 코드 저장
                with open(source_file_path, "w") as f:
                    f.write(code)

                # 컴파일 실행
                compile_result = subprocess.run(
                    [compiler, source_file_path, "-o", binary_path],
                    capture_output=True, text=True
                )

                if compile_result.returncode != 0:
                    return {"output": "", "error": compile_result.stderr}

                # 실행 (입력 데이터를 제공하여 `scanf()`가 입력을 기다리지 않도록 함)
                run_result = subprocess.run(
                    [binary_path],
                    input=input_data if input_data else "\n",  
                    capture_output=True, text=True, timeout=5,
                )

                return {"output": run_result.stdout, "error": run_result.stderr}

        except subprocess.TimeoutExpired:
            return {"output": "", "error": "Execution timed out (possible infinite loop)"}
        except Exception as e:
            return {"output": "", "error": str(e)}
