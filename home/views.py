"""Views for the Home app."""

import json
import requests

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST


def index(request):
    """Render the home page."""
    # Home is a static landing page with no dynamic query logic.
    return render(request, "home/index.html")


def _fallback_response(message):
    """Return a local fallback response when AI is unavailable."""
    responses = [
        {
            "match": ["casual", "weekend", "brunch", "relaxed"],
            "text": (
                "Try an oversized linen shirt, tapered trousers, and clean white trainers. "
                "Add a light knit for texture."
            ),
        },
        {
            "match": ["work", "meeting", "office", "professional"],
            "text": (
                "Go for a structured blazer, smooth cotton blouse, and straight-leg trousers. "
                "Finish with loafers or low heels."
            ),
        },
        {
            "match": ["date", "night", "dinner", "evening"],
            "text": (
                "Try a satin midi skirt, fitted knit top, and a soft draped coat. "
                "Add a statement earring for polish."
            ),
        },
        {
            "match": ["warm", "summer", "hot", "sunny"],
            "text": (
                "A breathable linen set or a cotton shirt dress works well. "
                "Pair with sandals and a lightweight tote."
            ),
        },
        {
            "match": ["cool", "chilly", "layers", "autumn"],
            "text": (
                "Layer a merino turtleneck under a wool coat with wide-leg trousers. "
                "Add a scarf for warmth."
            ),
        },
        {
            "match": ["neutral", "minimal", "classic"],
            "text": (
                "Build a tonal look with ivory, camel, and charcoal. "
                "Mix textures like knit, denim, and matte twill."
            ),
        },
        {
            "match": ["bold", "color", "colour", "statement"],
            "text": (
                "Start with a strong hue (saffron, cobalt, or olive) "
                "and keep the rest neutral. One hero piece is enough."
            ),
        },
    ]
    lowered = message.lower()
    for item in responses:
        if any(word in lowered for word in item["match"]):
            return item["text"]
    return (
        "Try a balanced look: soft top, structured bottom, and one texture pop. "
        "Want more detail on colour or occasion?"
    )


@require_POST
def style_assistant(request):
    """Handle style assistant messages via Gemini API."""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    api_key = settings.GEMINI_API_KEY
    if not api_key:
        return JsonResponse({"reply": _fallback_response(message)})

    system_prompt = (
        "You are the Fabric Focus style assistant. "
        "Suggest 2-3 outfit ideas with concise bullet-like lines, "
        "mention fabrics or textures, and ask one short follow-up question."
    )

    request_body = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": [
            {
                "role": "user",
                "parts": [{"text": message}],
            }
        ],
    }

    model = settings.GEMINI_MODEL
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

    try:
        response = requests.post(
            url,
            headers={
                "x-goog-api-key": api_key,
                "Content-Type": "application/json",
            },
            json=request_body,
            timeout=15,
        )
    except requests.RequestException:
        return JsonResponse({"reply": _fallback_response(message)})

    if not response.ok:
        return JsonResponse({"reply": _fallback_response(message)})

    data = response.json()
    reply = None
    candidates = data.get("candidates", [])
    if candidates:
        content = candidates[0].get("content", {})
        parts = content.get("parts", [])
        if parts:
            reply = parts[0].get("text")
    if not reply:
        reply = _fallback_response(message)

    return JsonResponse({"reply": reply})
