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


@require_POST
def style_assistant(request):
    """Handle style assistant messages via OpenAI."""
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (TypeError, json.JSONDecodeError):
        return JsonResponse({"error": "Invalid JSON payload."}, status=400)

    message = (payload.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "Message is required."}, status=400)

    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return JsonResponse(
            {"error": "AI is not configured. Set OPENAI_API_KEY."},
            status=503
        )

    system_prompt = (
        "You are the Fabric Focus style assistant. "
        "Suggest 2-3 outfit ideas with concise bullet-like lines, "
        "mention fabrics or textures, and ask one short follow-up question."
    )

    request_body = {
        "model": settings.OPENAI_MODEL,
        "input": [
            {
                "role": "system",
                "content": [{"type": "input_text", "text": system_prompt}],
            },
            {
                "role": "user",
                "content": [{"type": "input_text", "text": message}],
            },
        ],
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=request_body,
            timeout=15,
        )
    except requests.RequestException:
        return JsonResponse(
            {"error": "AI request failed. Please try again."},
            status=502
        )

    if not response.ok:
        return JsonResponse(
            {"error": "AI service error.", "details": response.text},
            status=response.status_code
        )

    data = response.json()
    reply = data.get("output_text")

    if not reply:
        for item in data.get("output", []):
            if item.get("type") == "message":
                for content in item.get("content", []):
                    if content.get("type") == "output_text":
                        reply = content.get("text")
                        break
            if reply:
                break

    if not reply:
        reply = "I can help with outfit ideas. Tell me the occasion and vibe."

    return JsonResponse({"reply": reply})
