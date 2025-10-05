#!/usr/bin/env python3
import requests
import os
from dotenv import load_dotenv

load_dotenv()


def get_user_id() -> str:
    backend_url = os.getenv('BACKEND_URL', 'http://localhost')
    port = os.getenv('PORT', '8001')
    url = f"{backend_url}:{port}/api/v1/auth/me"
    print(f"Making request to: {url}")

    try:
        res = requests.get(
            url,
            headers={"Authorization": f"Bearer {os.getenv('AUTH_TOKEN', 'UCJ0oLMIqSYgLVOAGp8aDu7TjhiRSYhu')}"}
        )
        if res.status_code == 401:
            print("❌ Unauthorized (401) — check your token.")
            return ""
        elif res.status_code == 404:
            print("❌ Endpoint not found (404). Check the URL.")
            return ""
        elif res.status_code >= 500:
            print("❌ Server error (500+). Try again later.")
            return ""

        data = res.json()
        user_id = data.get("id")
        print(f"Received user ID: {user_id}")
        return user_id

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return ""


def make_api_call(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    backend_url = os.getenv('BACKEND_URL', 'http://localhost')
    port = os.getenv('PORT', '8001')
    url = f"{backend_url}:{port}/api/v1{endpoint}" if not endpoint.startswith("/") else f"{backend_url}:{port}/api/v1{endpoint}"
    headers = {"Authorization": f"Bearer {os.getenv('AUTH_TOKEN', 'UCJ0oLMIqSYgLVOAGp8aDu7TjhiRSYhu')}"}

    try:
        if method.upper() == "GET":
            res = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            res = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError("Unsupported HTTP method")

        if res.status_code == 401:
            print("❌ Unauthorized (401) — check your token.")
            return {}
        elif res.status_code == 404:
            print("❌ Endpoint not found (404). Check your route.")
            return {}
        elif res.status_code >= 500:
            print("❌ Server error (500+). Try again later.")
            return {}

        return res.json()

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {}
    except ValueError as e:
        print(f"❌ Error: {e}")
        return {}


# --- optional placeholders for later use ---

def get_all_projects_for_user(user_id: str) -> list[str]:
    data = make_api_call(f"/users/{user_id}/projects", "GET")
    return [p.get("id") for p in data.get("projects", [])]


def save_context_to_project(user_id: str, project_id: str, context: str) -> None:
    data = {"user_id": user_id, "context": context}
    make_api_call(f"/projects/{project_id}/context", "POST", data=data)


def get_relevant_context(user_id: str, project_id: str, prompt: str) -> list[str]:
    data = {"user_id": user_id, "prompt": prompt}
    res = make_api_call(f"/projects/{project_id}/context/search", "POST", data=data)
    return res.get("contexts", [])


# --- main test ---
if __name__ == "__main__":
    user_id = get_user_id()
    print("User ID:", user_id)

    payload = {'name': "tim nigga", 'description': "jk"}
    response = make_api_call("/projects", "POST", data=payload)
    print("Response:", response)
    response = make_api_call(f"/projects", "GET")
    print("Response:", response)
