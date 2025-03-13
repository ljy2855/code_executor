import os
import subprocess
import tempfile


class Executor:
    """각 언어별 코드 실행기"""

    def __init__(self, language):
        self.language = language

    async def execute(self, task):
        """언어별 실행 함수 매핑"""
        execute_methods = {
            "python": self._execute_python,
            "java": self._execute_java,
            "c": self._execute_c,
            "cpp": self._execute_cpp,
        }
        if self.language in execute_methods:
            return await execute_methods[self.language](task)
        return {"output": "", "error": f"Unsupported language: {self.language}"}

    async def _execute_python(self, task):
        """Python 코드 실행"""
        return await self._execute_code(task, "python3", ".py")

    async def _execute_java(self, task):
        """Java 코드 실행"""
        task_id = task["task_id"]
        code = task["code"]
        input_data = task.get("input", "")

        print(f"[Worker] Executing Java task {task_id}")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                java_file_path = os.path.join(temp_dir, "Main.java")

                # Java 코드 저장 (파일명은 반드시 Main.java)
                with open(java_file_path, "w") as f:
                    f.write(code)

                # Java 코드 컴파일
                compile_result = subprocess.run(["javac", java_file_path], capture_output=True, text=True)
                if compile_result.returncode != 0:
                    return {"output": "", "error": compile_result.stderr}

                # 실행 (파일명이 `Main.java`이므로 `java Main` 실행)
                run_result = subprocess.run(
                    ["java", "-cp", temp_dir, "Main"],
                    input=input_data, capture_output=True, text=True
                )

                return {"output": run_result.stdout, "error": run_result.stderr}

        except Exception as e:
            return {"output": "", "error": str(e)}

    async def _execute_c(self, task):
        """C 코드 실행"""
        return await self._execute_compiled(task, "gcc", ".c")

    async def _execute_cpp(self, task):
        """C++ 코드 실행"""
        return await self._execute_compiled(task, "g++", ".cpp")

    async def _execute_code(self, task, interpreter, extension):
        """스크립트 언어 (Python) 실행"""
        task_id = task["task_id"]
        code = task["code"]
        input_data = task.get("input", "")

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
            os.remove(temp_file_path)

    async def _execute_compiled(self, task, compiler, extension):
        """컴파일 언어 (C, C++) 실행"""
        task_id = task["task_id"]
        code = task["code"]
        input_data = task.get("input", "")

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

                # 실행 (입력 데이터를 제공하여 scanf()가 입력을 기다리지 않도록 함)
                run_result = subprocess.run(
                    [binary_path],
                    input=input_data if input_data else "\n",  # 입력이 없으면 개행 전달
                    capture_output=True, text=True, timeout=5,  # 실행 시간 제한
                )

                return {"output": run_result.stdout, "error": run_result.stderr}

        except subprocess.TimeoutExpired:
            return {"output": "", "error": "Execution timed out (possible infinite loop)"}
        except Exception as e:
            return {"output": "", "error": str(e)}