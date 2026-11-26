import requests

from core.config import SERVER_URL
from database import crud

TIMEOUT = 10


class WebClientError(Exception):
    """Custom exception class representing errors in the networking layer."""

    def __init__(self, message, status_code=None, original_exception=None):
        super().__init__(message)
        self.status_code = status_code
        self.original_exception = original_exception


def _auth_headers(require_auth=False):
    session = crud.get_session()
    if session and session.get("access_token"):
        return {"Authorization": f"Bearer {session['access_token']}"}
    if require_auth:
        raise WebClientError(
            "You must be signed in to perform this action.", status_code=401
        )
    return {}


def _request(method, endpoint, require_auth=False, **kwargs):
    """Reusable request wrapper targeting the unified vor-backend API."""
    url = f"{SERVER_URL.rstrip('/')}/{endpoint.lstrip('/')}"

    headers = dict(kwargs.pop("headers", {}) or {})
    headers.update(_auth_headers(require_auth=require_auth))
    if headers:
        kwargs["headers"] = headers

    if "timeout" not in kwargs:
        kwargs["timeout"] = TIMEOUT

    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()

        try:
            return response.json()
        except ValueError as e:
            raise WebClientError(
                "Invalid response format from server (expected JSON)",
                status_code=response.status_code,
                original_exception=e,
            )

    except requests.exceptions.Timeout as e:
        raise WebClientError(
            "Connection timed out. Please try again.", original_exception=e
        )
    except requests.exceptions.ConnectionError as e:
        raise WebClientError(
            f"Cannot connect to server ({SERVER_URL}). Please check if the backend is running.",
            original_exception=e,
        )
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if e.response is not None else None
        detail = "An error occurred on the server."
        if e.response is not None:
            try:
                err_data = e.response.json()
                if isinstance(err_data, dict):
                    detail = err_data.get("detail") or err_data.get("message") or detail
            except Exception:
                detail = e.response.text or detail
        raise WebClientError(detail, status_code=status_code, original_exception=e)
    except requests.exceptions.RequestException as e:
        raise WebClientError(f"Network request failed: {str(e)}", original_exception=e)


def get_jobs():
    """Retrieves all job listings from vor-backend. GET /api/v1/jobs"""
    return _request("GET", "api/v1/jobs")


def get_job_detail(job_id):
    """Retrieves detailed info for a single job. GET /api/v1/jobs/{job_id}"""
    return _request("GET", f"api/v1/jobs/{job_id}")


def apply_job(job_id, email=None, display_name=None, major=None, student_year=1):
    """Submits a job application as the authenticated student. POST /api/v1/jobs/{job_id}/apply"""
    payload = {
        "display_name": display_name,
        "major": major,
        "student_year": student_year,
    }
    return _request(
        "POST", f"api/v1/jobs/{job_id}/apply", require_auth=True, json=payload
    )


def get_applications(email=None):
    """Retrieves all job IDs applied to by the authenticated student. GET /api/v1/applications/me"""
    return _request("GET", "api/v1/applications/me", require_auth=True)


def sync_cv(payload):
    """Syncs the authenticated student's CV profile to vor-backend. POST /api/v1/cvs"""
    return _request("POST", "api/v1/cvs", require_auth=True, json=payload)
