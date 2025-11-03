import subprocess
import tempfile
import os
import json

class CodeExecutor:
    @staticmethod
    def execute_python(code: str, test_input: str = "") -> dict:
        """Execute Python code safely"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            try:
                result = subprocess.run(
                    ['python', temp_file],
                    input=test_input,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr
                }
            finally:
                os.unlink(temp_file)
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Execution timed out (5 seconds limit)"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    @staticmethod
    def execute_java(code: str, test_input: str = "") -> dict:
        """Execute Java code safely"""
        try:
            # Extract class name from code
            import re
            class_match = re.search(r'public\s+class\s+(\w+)', code)
            if not class_match:
                return {
                    "success": False,
                    "output": "",
                    "error": "Could not find public class declaration"
                }
            
            class_name = class_match.group(1)
            
            # Create temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                java_file = os.path.join(temp_dir, f"{class_name}.java")
                
                with open(java_file, 'w') as f:
                    f.write(code)
                
                # Compile
                compile_result = subprocess.run(
                    ['javac', java_file],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if compile_result.returncode != 0:
                    return {
                        "success": False,
                        "output": "",
                        "error": f"Compilation error: {compile_result.stderr}"
                    }
                
                # Execute
                run_result = subprocess.run(
                    ['java', '-cp', temp_dir, class_name],
                    input=test_input,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                return {
                    "success": run_result.returncode == 0,
                    "output": run_result.stdout,
                    "error": run_result.stderr
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "output": "",
                "error": "Execution timed out"
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }
    
    @staticmethod
    def execute_code(code: str, language: str, test_input: str = "") -> dict:
        """Execute code based on language"""
        if language.lower() == "python":
            return CodeExecutor.execute_python(code, test_input)
        elif language.lower() == "java":
            return CodeExecutor.execute_java(code, test_input)
        else:
            return {
                "success": False,
                "output": "",
                "error": f"Unsupported language: {language}"
            }

code_executor = CodeExecutor()