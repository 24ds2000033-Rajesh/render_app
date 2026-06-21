import re
import sys
import traceback
from io import StringIO
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CodeRequest(BaseModel):
    code: str


class CodeResponse(BaseModel):
    error: List[int]
    result: str


def execute_python_code(code: str):
    """
    Execute Python code and return exact output.
    """

    old_stdout = sys.stdout
    old_stderr = sys.stderr

    stdout_buffer = StringIO()
    stderr_buffer = StringIO()

    sys.stdout = stdout_buffer
    sys.stderr = stderr_buffer

    try:
        exec(code, {})

        return {
            "success": True,
            "output": stdout_buffer.getvalue()
        }

    except Exception:
        return {
            "success": False,
            "output": traceback.format_exc()
        }

    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def analyze_error(traceback_text: str):
    """
    Extract line numbers from traceback.
    """

    matches = re.findall(r'line (\d+)', traceback_text)

    lines = []
    for m in matches:
        try:
            lines.append(int(m))
        except Exception:
            pass

    return sorted(list(set(lines)))


@app.get("/")
def root():
    return {"status": "running"}


@app.post("/code-interpreter", response_model=CodeResponse)
def code_interpreter(req: CodeRequest):

    execution = execute_python_code(req.code)

    if execution["success"]:
        return {
            "error": [],
            "result": execution["output"]
        }

    return {
        "error": analyze_error(execution["output"]),
        "result": execution["output"]
    }
