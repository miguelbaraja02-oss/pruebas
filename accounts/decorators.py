# accounts/decorators.py
from django.shortcuts import redirect
from functools import wraps

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            # 1. Debe estar logueado
            if not request.user.is_authenticated:
                return redirect("accounts:login")

            # 2. Debe tener perfil y rol
            if not hasattr(request.user, "profile") or not request.user.profile.role:
                return redirect("accounts:welcome")

            # 3. Compara por NOMBRE del rol
            if request.user.profile.role.name not in allowed_roles:
                return redirect("accounts:welcome")

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator

