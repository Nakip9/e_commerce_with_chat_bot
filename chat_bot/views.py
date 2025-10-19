from __future__ import annotations

import json
import logging
import re
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from .models import Chat
from market.models import Car


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


ARABIC_GREETING = (
    "مرحبًا! أنا مساعد مبيعات AutoDrive. يمكنني مساعدتك في:"
)

ARABIC_DEFAULT_OPTIONS = (
    "\n1- استعراض السيارات المتوفرة لدينا."
    "\n2- طرح أسئلة عامة حول خدماتنا وعروض التمويل."
    "\nأدخل رقم الاختيار أو اكتب سؤالك بالعربية."
)

DEFAULT_ASSISTANT_GREETING = ARABIC_GREETING + ARABIC_DEFAULT_OPTIONS


def _normalize_eastern_digits(text: str) -> str:
    translation_table = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")
    return text.translate(translation_table)


def _extract_first_integer(text: str) -> int | None:
    match = re.search(r"\d+", text)
    if not match:
        return None
    try:
        return int(match.group(0))
    except ValueError:  # pragma: no cover - defensive
        return None


def _format_car_summary(cars: Iterable[Car]) -> str:
    cars_list = list(cars)
    if not cars_list:
        return (
            "نعتذر، لا توجد سيارات متاحة في الوقت الحالي. "
            "سنقوم بتحديثك بمجرد توفر سيارات جديدة."
        )

    lines = [
        "هذه قائمة سياراتنا الحالية:",
    ]
    for index, car in enumerate(cars_list, start=1):
        lines.append(f"{index}- {car.name_ar}")

    lines.append(
        "للحصول على تفاصيل سيارة معينة، أدخل رقم السيارة أو عبارة مثل 'سيارة 2'."
    )
    return "\n".join(lines)


def _format_car_details(car_index: int) -> str:
    cars = list(Car.objects.all())
    if not cars:
        return (
            "حاليًا لا توجد سيارات متاحة للعرض. يمكنك معاودة المحاولة لاحقًا."
        )

    if car_index < 1 or car_index > len(cars):
        return (
            "لم أجد سيارة بالرقم المطلوب. يرجى اختيار رقم من 1 إلى "
            f"{len(cars)} أو كتابة سؤالك بالعربية."
        )

    car = cars[car_index - 1]
    details = [
        f"سيارة رقم {car_index}: {car.name_ar}",
        f"السعر: {car.price_ar}",
        "أبرز المواصفات:",
        f"- {car.feature_one_ar}",
        f"- {car.feature_two_ar}",
        f"- {car.feature_three_ar}",
        "هل ترغب في معرفة خيارات تمويل أو سيارات أخرى؟",
    ]
    return "\n".join(details)


def ask_bot(message: str, *, previous_response: str | None = None) -> str:
    cleaned = message.strip()
    if not cleaned:
        raise ValueError("Message cannot be empty.")

    normalized = _normalize_eastern_digits(cleaned)
    lowered = normalized.lower()

    if "عرض" in lowered and "سيارات" in lowered:
        return _format_car_summary(Car.objects.all())

    choice = _extract_first_integer(lowered)
    if choice is not None:
        plain_choice = re.fullmatch(r"\s*1[\s\-\.)]*\s*", lowered)
        if choice == 1 and plain_choice:
            if previous_response and "أدخل رقم السيارة" in previous_response:
                return _format_car_details(choice)
            return _format_car_summary(Car.objects.all())
        if previous_response and "سياراتنا الحالية" in previous_response:
            return _format_car_details(choice)
        if "سيارة" in lowered or "تفاصيل" in lowered:
            return _format_car_details(choice)
        if choice != 1:
            return _format_car_details(choice)

    messages = [
        {"role": "system", "content": settings.OPENROUTER_SYSTEM_PROMPT},
        {"role": "system", "content": DEFAULT_ASSISTANT_GREETING},
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

        previous_chat = (
            Chat.objects.filter(user=request.user)
            .order_by("-created_at")
            .first()
        )

        previous_response = previous_chat.response if previous_chat else None

        try:
            response_text = ask_bot(message, previous_response=previous_response)
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

    return render(
        request,
        "chatbot.html",
        {"chats": chats, "default_message": DEFAULT_ASSISTANT_GREETING},
    )
