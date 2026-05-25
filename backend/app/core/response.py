import uuid
from typing import Optional


def success_response(message: str, data=None) -> dict:
    return {
        "success": True,
        "code": 200,
        "message": message,
        "data": data,
        "traceId": str(uuid.uuid4())
    }


def error_response(code: int, message: str) -> dict:
    return {
        "success": False,
        "code": code,
        "message": message,
        "data": None,
        "traceId": str(uuid.uuid4())
    }
