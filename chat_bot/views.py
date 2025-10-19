from __future__ import annotations

import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Chat


logger = logging.getLogger(__name__)


class ChatServiceError(RuntimeError):
    """Raised when the assistant cannot produce a response."""


def _call_openrouter(messages: list[dict[str, str]]) -> str:
    if not settings.OPENROUTER_API_KEY:
        raise ChatServiceError(
            "The assistant is missing an API key. Please configure the chatbot first."
        )

    endpoint = settings.OPENROUTER_BASE_URL.rstrip("/") + "/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if settings.OPENROUTER_SITE_URL:
        headers["HTTP-Referer"] = settings.OPENROUTER_SITE_URL
    if settings.OPENROUTER_APP_NAME:
        headers["X-Title"] = settings.OPENROUTER_APP_NAME

    payload = json.dumps(
        {
            "model": settings.OPENROUTER_MODEL,
            "messages": messages,
            "temperature": settings.OPENROUTER_TEMPERATURE,
            "max_tokens": settings.OPENROUTER_MAX_TOKENS,
        }
    ).encode("utf-8")

    request = Request(endpoint, data=payload, headers=headers, method="POST")

    try:
        with urlopen(request, timeout=settings.OPENROUTER_TIMEOUT) as response:
            body = response.read()
            try:
                payload_json: dict[str, Any] = json.loads(body.decode("utf-8"))
            except json.JSONDecodeError as exc:
                logger.warning(
                    "OpenRouter sent a non-JSON response: %s", body[:200]
                )
                raise ChatServiceError(
                    "The assistant returned an unreadable response. Please try again later."
                ) from exc
    except HTTPError as exc:
        raw_error = exc.read()
        try:
            detail: Any = json.loads(raw_error.decode("utf-8"))
        except Exception:  # noqa: BLE001
            detail = raw_error.decode("utf-8", errors="ignore")
        logger.warning("OpenRouter returned an error %s: %s", exc.code, detail)
        raise ChatServiceError(
            "The assistant is temporarily unavailable. Please try again shortly."
        ) from exc
    except URLError as exc:
        logger.exception("OpenRouter request failed")
        raise ChatServiceError(
            "I couldn't reach the assistant right now. Please try again in a moment."
        ) from exc

    try:
        content = payload_json["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError) as exc:
        logger.warning("Unexpected OpenRouter payload structure: %s", payload_json)
        raise ChatServiceError(
            "The assistant sent an unexpected response. Please try again later."
        ) from exc

    if not content:
        raise ChatServiceError(
            "The assistant responded with an empty message. Please try again."
        )

    return content


def ask_bot(message: str) -> str:
    cleaned = message.strip()
    if not cleaned:
        raise ValueError("Message cannot be empty.")

    messages = [
        {"role": "system", "content": settings.OPENROUTER_SYSTEM_PROMPT},
        {"role": "user", "content": cleaned},
    ]

    return _call_openrouter(messages)


def chatbot(request: HttpRequest) -> HttpResponse:
    if request.user.is_authenticated:
        chats = Chat.objects.filter(user=request.user).order_by("created_at")
    else:
        chats = Chat.objects.none()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Please sign in to chat with the assistant."}, status=403
            )

        message = request.POST.get("message", "")

        if not message or not message.strip():
            return JsonResponse(
                {"error": "Please enter a message before sending."}, status=400
            )

        try:
            response_text = ask_bot(message)
        except ValueError:
            return JsonResponse(
                {"error": "Please enter a message before sending."}, status=400
            )
        except ChatServiceError as exc:
            return JsonResponse({"error": str(exc)}, status=502)

        chat = Chat.objects.create(
            user=request.user,
            message=message,
            response=response_text,
        )

        return JsonResponse(
            {
                "message": chat.message,
                "response": chat.response,
            }
        )

    return render(request, "chatbot.html", {"chats": chats})
