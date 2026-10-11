"""MiniMax H3 request and task-status boundaries."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from client import MiniMaxH3Client, MiniMaxH3Error


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.headers = {"x-trace-id": "trace-minimax"}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.payload).encode()


@pytest.mark.asyncio
async def test_submit_sends_one_async_text_video_request():
    calls = []

    def fake_open(request, timeout):
        calls.append((request.full_url, json.loads(request.data), timeout))
        return FakeResponse({"task_id": "task-123", "trace_id": "trace-submit"})

    with patch("client.OPENER.open", side_effect=fake_open):
        result = await MiniMaxH3Client("test-key").submit("A paper kite rises")
    assert calls == [
        (
            "https://api.acedata.cloud/minimax/videos",
            {
                "model": "MiniMax-H3",
                "content": [{"type": "text", "text": "A paper kite rises"}],
                "resolution": "768P",
                "duration": 4,
                "ratio": "16:9",
                "async": True,
            },
            90,
        )
    ]
    assert result["status"] == "submitted"
    assert result["task_id"] == "task-123"
    assert result["trace_id"] == "trace-submit"
    assert "video_url" not in result


@pytest.mark.asyncio
async def test_first_frame_uses_adaptive_ratio():
    with patch(
        "client.OPENER.open", return_value=FakeResponse({"task_id": "task-456"})
    ) as opening:
        await MiniMaxH3Client("test-key").submit(
            "A kite rises", image_url="https://example.org/kite.png"
        )
    payload = json.loads(opening.call_args.args[0].data)
    assert payload["ratio"] == "adaptive"
    assert payload["content"] == [
        {"type": "text", "text": "A kite rises"},
        {
            "type": "image_url",
            "image_url": {"url": "https://example.org/kite.png"},
            "role": "first_frame",
        },
    ]


@pytest.mark.asyncio
async def test_query_waits_for_succeeded_and_withholds_internal_data():
    pending = {"task": {"id": "task-123", "status": "running", "content": {}}}
    finished = {
        "task": {
            "id": "task-123",
            "status": "succeeded",
            "content": {"url": "https://cdn.example.org/final.mp4"},
            "resolution": "768P",
            "duration": 4,
            "usage": {
                "total_seconds": 4,
                "output_seconds": 4,
                "input_seconds": 0,
                "input_image_count": 0,
                "supplier": "internal-only",
            },
        }
    }
    failed = {
        "task": {
            "id": "task-123",
            "status": "failed",
            "content": {"url": "https://cdn.example.org/preview.mp4"},
        }
    }
    with patch(
        "client.OPENER.open",
        side_effect=[
            FakeResponse(pending),
            FakeResponse(finished),
            FakeResponse(failed),
        ],
    ) as opening:
        first = await MiniMaxH3Client("test-key").query("task-123")
        last = await MiniMaxH3Client("test-key").query("task-123")
        unsuccessful = await MiniMaxH3Client("test-key").query("task-123")
    assert opening.call_count == 3
    assert first["status"] == "pending"
    assert first["video_url"] == ""
    assert last["status"] == "succeeded"
    assert last["video_url"] == "https://cdn.example.org/final.mp4"
    assert last["usage"] == {
        "total_seconds": 4,
        "output_seconds": 4,
        "input_seconds": 0,
        "input_image_count": 0,
    }
    assert "supplier" not in str(last)
    assert unsuccessful["status"] == "failed"
    assert unsuccessful["video_url"] == ""


@pytest.mark.asyncio
async def test_invalid_inputs_never_submit_a_paid_job():
    client = MiniMaxH3Client("test-key")
    for kwargs in (
        {"prompt": " "},
        {"prompt": "A kite", "duration": 3},
        {"prompt": "A kite", "resolution": "720P"},
        {"prompt": "A kite", "ratio": "adaptive"},
        {"prompt": "A kite", "image_url": "http://example.org/kite.png"},
    ):
        with patch("client.OPENER.open") as opening, pytest.raises(MiniMaxH3Error):
            await client.submit(**kwargs)
        assert opening.call_count == 0
