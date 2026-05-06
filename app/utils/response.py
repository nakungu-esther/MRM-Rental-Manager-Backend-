"""
Standardized API response utilities
Global format:
  Success: {"success": true, "message": "...", "data": {...}}
  Error:   {"success": false, "message": "...", "errors": [...]}
"""
from typing import Any, Optional, List
from fastapi import HTTPException


def success_response(data: Any = None, message: Optional[str] = None) -> dict:
    """Return standardized success response"""
    response = {"success": True}
    if message:
        response["message"] = message
    if data is not None:
        response["data"] = data
    return response


def error_response(message: str, errors: Optional[List[str]] = None, status_code: int = 400) -> HTTPException:
    """Return standardized error as HTTPException"""
    content = {"success": False, "message": message}
    if errors:
        content["errors"] = errors
    return HTTPException(status_code=status_code, detail=content)


def not_found_error(resource: str = "Resource") -> HTTPException:
    """Return standardized 404 error"""
    return error_response(f"{resource} not found.", status_code=404)


def forbidden_error(message: str = "Access denied.") -> HTTPException:
    """Return standardized 403 error"""
    return error_response(message, status_code=403)


def validation_error(errors: List[str]) -> HTTPException:
    """Return standardized 422 validation error"""
    return error_response("Validation failed.", errors=errors, status_code=422)
