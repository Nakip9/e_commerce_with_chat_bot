from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
import re
from typing import Final

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render

from market.models import Car
from .models import Chat


@dataclass(frozen=True)
class BotReply:
    """Container for bot responses returned to the UI."""

    message: str
    sources: tuple[str, ...] = ()


_GREETINGS: Final[tuple[str, ...]] = (
    "hi",
    "hello",
    "hey",
    "good morning",
    "good afternoon",
    "good evening",
)


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _format_currency(value: str) -> str:
    """Ensure currency output has spacing consistent across answers."""
    return value.replace("USD", "USD ").replace("SAR", "SAR ")


def _match_car_by_name(message: str, cars: Iterable[Car]) -> Car | None:
    message_lower = message.lower()
    for car in cars:
        if car.name_en.lower() in message_lower or car.slug in message_lower:
            return car
    return None


def ask_bot(message: str) -> BotReply:
    """Return a deterministic response for the provided message.

    The implementation focuses on product discovery rather than relying on
    external APIs. This keeps the chatbot functional in offline
    environments and avoids the need for additional credentials.
    """

    cleaned = _normalise(message)
    cars = list(Car.objects.all())

    if not cleaned:
        return BotReply(
            "I didn't catch that. Please enter a question about our cars or services."
        )

    if any(cleaned.startswith(greeting) for greeting in _GREETINGS):
        return BotReply(
            "Hello! I can help you discover vehicles, pricing and services at AutoDrive Market."
        )

    if "inventory" in cleaned or "available" in cleaned or "cars" in cleaned:
        if not cars:
            return BotReply("Our inventory is being updated. Please check back shortly.")
        summary = ", ".join(car.name_en for car in cars)
        return BotReply(
            f"We currently feature these models: {summary}. Let me know if you'd like details on any of them.",
            tuple(car.slug for car in cars),
        )

    matched_car = _match_car_by_name(cleaned, cars)
    if matched_car is not None:
        features = ", ".join(
            feature
            for feature in (
                matched_car.feature_one_en,
                matched_car.feature_two_en,
                matched_car.feature_three_en,
            )
            if feature
        )
        return BotReply(
            " ".join(
                [
                    f"The {matched_car.name_en} is priced at {_format_currency(matched_car.price_en)}.",
                    f"Key highlights include {features}.",
                    "Would you like to schedule a test drive?",
                ]
            ),
            (matched_car.slug,),
        )

    if "test drive" in cleaned or "book" in cleaned:
        return BotReply(
            "You can book a test drive directly from the vehicle page by selecting 'Book a test drive' and sharing your preferred schedule."
        )

    if "finance" in cleaned or "payment" in cleaned:
        return BotReply(
            "We partner with several banks and offer in-house financing with instant approval. Let us know your budget and we will prepare options for you."
        )

    return BotReply(
        "I'm here to help with inventory, pricing, services, and test drive bookings. Could you rephrase your question?"
    )


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
        reply = ask_bot(message)

        chat = Chat.objects.create(
            user=request.user,
            message=message,
            response=reply.message,
        )

        return JsonResponse(
            {
                "message": chat.message,
                "response": reply.message,
                "sources": list(reply.sources),
            }
        )

    return render(request, "chatbot.html", {"chats": chats})
