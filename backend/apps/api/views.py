"""Simple root view with API status."""

from django.http import JsonResponse


def root_view(request):
    """Return API status and available endpoints."""
    return JsonResponse(
        {
            "name": "News Aggregator API",
            "version": "0.1.0",
            "status": "running",
            "endpoints": {
                "news_list": "/api/news/",
                "news_detail": "/api/news/{id}/",
                "sources": "/api/sources/",
                "categories": "/api/categories/",
                "auth_login": "/api/auth/login/",
                "auth_refresh": "/api/auth/refresh/",
                "admin": "/admin/",
            },
        },
        json_dumps_params={"indent": 2, "ensure_ascii": False},
    )
