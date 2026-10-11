"""Bounded MiniMax H3 submission and existing-task lookup for AstrBot."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

API_BASE = "https://api.acedata.cloud"
RESOLUTIONS = {"768P", "2K"}
RATIOS = {"21:9", "16:9", "4:3", "1:1", "3:4", "9:16"}
FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}


class _NoRedirect(HTTPRedirectHandler):
    """Never forward the configured key to another host."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        return None


OPENER = build_opener(_NoRedirect)


class MiniMaxH3Error(RuntimeError):
    """An error safe to return to an AstrBot conversation."""


def _valid_https_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.netloc
        and not parsed.username
        and not parsed.password
    )


class MiniMaxH3Client:
    """Submit one video or query a prior MiniMax H3 task."""

    def __init__(self, api_key: str) -> None:
        token = api_key.strip()
        if (
            not token
            or token.lower().startswith("bearer ")
            or token.startswith("platform-")
        ):
            raise MiniMaxH3Error(
                "Set an Ace Data Cloud generation API key in plugin settings."
            )
        self._api_key = token

    def _post(self, path: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
        request = Request(
            API_BASE + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "AceDataCloudAstrBot/0.1.0",
            },
            method="POST",
        )
        try:
            with OPENER.open(request, timeout=90) as response:
                body = json.load(response)
                header_trace = response.headers.get(
                    "x-trace-id", ""
                ) or response.headers.get("x-request-id", "")
        except HTTPError as exc:
            raise MiniMaxH3Error(
                f"Ace Data Cloud returned HTTP {exc.code}. Check service access and request history."
            ) from None
        except (URLError, TimeoutError, OSError):
            raise MiniMaxH3Error(
                "The API connection failed. Check request history before submitting another video."
            ) from None
        except (ValueError, UnicodeError):
            raise MiniMaxH3Error(
                "The API returned invalid JSON. Check request history before retrying."
            ) from None
        if not isinstance(body, dict):
            raise MiniMaxH3Error("The API returned an unexpected response format.")
        return body, str(body.get("trace_id") or header_trace)

    async def submit(
        self,
        prompt: str,
        duration: int = 4,
        resolution: str = "768P",
        ratio: str = "",
        image_url: str = "",
    ) -> dict[str, Any]:
        """Submit one asynchronous text or first-frame video without retrying."""
        prompt = prompt.strip()
        if not prompt or len(prompt) > 7000:
            raise MiniMaxH3Error("Provide a video prompt of 1–7000 characters.")
        if (
            not isinstance(duration, int)
            or isinstance(duration, bool)
            or not 4 <= duration <= 15
        ):
            raise MiniMaxH3Error("Duration must be 4–15 seconds.")
        if resolution not in RESOLUTIONS:
            raise MiniMaxH3Error("Resolution must be 768P or 2K.")
        if image_url and not _valid_https_url(image_url):
            raise MiniMaxH3Error("Provide an authorized HTTPS first-frame image URL.")
        if not ratio:
            ratio = "adaptive" if image_url else "16:9"
        if ratio not in (RATIOS | {"adaptive"} if image_url else RATIOS):
            raise MiniMaxH3Error("Choose a model-supported aspect ratio.")
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        if image_url:
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": image_url},
                    "role": "first_frame",
                }
            )
        payload = {
            "model": "MiniMax-H3",
            "content": content,
            "resolution": resolution,
            "duration": duration,
            "ratio": ratio,
            "async": True,
        }
        body, trace_id = await asyncio.to_thread(self._post, "/minimax/videos", payload)
        if body.get("success") is False or body.get("error"):
            raise MiniMaxH3Error(
                "Video submission was rejected. Check request history before trying again."
            )
        task_id = body.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise MiniMaxH3Error(
                "No task ID was returned. Check request history before submitting again."
            )
        return {
            "status": "submitted",
            "task_id": task_id,
            "trace_id": trace_id,
            "next_step": "Query this same task ID; do not submit another video while it is pending.",
        }

    async def query(self, task_id: str) -> dict[str, Any]:
        """Return task.content.url only after the task reports succeeded."""
        task_id = task_id.strip()
        if not task_id or len(task_id) > 128:
            raise MiniMaxH3Error("Pass the exact task ID from MiniMax H3 submission.")
        body, trace_id = await asyncio.to_thread(
            self._post, "/minimax/tasks", {"id": task_id, "action": "retrieve"}
        )
        if body.get("success") is False or body.get("error"):
            raise MiniMaxH3Error("Task lookup failed. Check request history.")
        task = body.get("task")
        if not isinstance(task, dict):
            raise MiniMaxH3Error("The API returned no task record.")
        status = str(task.get("status") or "").lower()
        content = task.get("content")
        video_url = content.get("url") if isinstance(content, dict) else None
        if status in FAILED:
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "failed",
                "success": False,
                "video_url": "",
            }
        if status != "succeeded":
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "pending",
                "success": False,
                "video_url": "",
            }
        if not isinstance(video_url, str) or not _valid_https_url(video_url):
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "failed",
                "success": False,
                "video_url": "",
            }
        usage = task.get("usage")
        public_usage = (
            {
                key: usage[key]
                for key in (
                    "total_seconds",
                    "input_seconds",
                    "output_seconds",
                    "input_image_count",
                )
                if key in usage
            }
            if isinstance(usage, dict)
            else {}
        )
        return {
            "task_id": task_id,
            "trace_id": trace_id,
            "status": "succeeded",
            "success": True,
            "video_url": video_url,
            "resolution": str(task.get("resolution") or ""),
            "duration": task.get("duration"),
            "usage": public_usage,
        }
