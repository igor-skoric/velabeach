import json
from django.utils.safestring import mark_safe


def user_json(request):
    if not request.user.is_authenticated:
        return {"user_json": mark_safe(json.dumps({"role": "anonymous"}))}

    user = request.user
    role = getattr(user, "role", None)

    if not role:
        if user.is_superuser:
            role = "admin"
        elif user.is_staff:
            role = "moderator"
        else:
            role = "user"

    user_data = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "role": role,
        "stage": user.stage.name if user.stage else 1
    }

    return {"user_json": mark_safe(json.dumps(user_data))}
