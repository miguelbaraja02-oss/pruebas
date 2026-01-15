# accounts/decorators.py
from functools import wraps

from django.shortcuts import redirect


def _user_role(request):
    """Helper to safely get the user's role or None."""
    if not hasattr(request.user, "profile"):
        return None
    return getattr(request.user.profile, "role", None)


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")

            if request.user.username == "root" or getattr(request.user, "is_superuser", False):
                return view_func(request, *args, **kwargs)

            role = _user_role(request)
            if not role:
                return redirect("accounts:welcome")

            if role.name not in allowed_roles:
                return redirect("accounts:welcome")

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def permission_required(permission_codes):
    """
    Permite acceder si el rol del usuario tiene al menos uno de los
    permisos indicados. Superusuarios y root pasan siempre.
    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("accounts:login")

            if request.user.username == "root" or getattr(request.user, "is_superuser", False):
                return view_func(request, *args, **kwargs)

            role = _user_role(request)
            if not role:
                return redirect("accounts:welcome")

            role_permissions = set(role.permissions.values_list("code", flat=True))
            if not role_permissions.intersection(set(permission_codes)):
                return redirect("accounts:welcome")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator

