# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django import forms

from .models import Profile
from .forms import ProfileForm, RoleForm
from .decorators import role_required


# ------------------- FORMULARIO DE REGISTRO -------------------
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Quitar textos de ayuda
        self.fields["username"].help_text = None
        self.fields["password1"].help_text = None
        self.fields["password2"].help_text = None

        # Agregar clases Bootstrap
        for field in self.fields:
            self.fields[field].widget.attrs.update({"class": "form-control"})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            Profile.objects.get_or_create(user=user)

        return user


# ------------------- LOGIN -------------------
def login_view(request):
    login_error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("accounts:welcome")
        else:
            request.session["login_error"] = "Usuario o contraseña incorrectos"
            return redirect("accounts:login")

    login_error = request.session.pop("login_error", None)
    return render(request, "accounts/login.html", {"login_error": login_error})


# ------------------- REGISTRO -------------------
def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:login")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


# ------------------- LOGOUT -------------------
@login_required(login_url="accounts:login")
def logout_view(request):
    logout(request)
    return redirect("accounts:login")


# ------------------- VISTAS AUTENTICADAS -------------------
@login_required(login_url="accounts:login")
def home(request):
    return render(request, "accounts/home.html")


@login_required(login_url="accounts:login")
def welcome_view(request):
    return render(request, "accounts/welcome.html")


@login_required(login_url="accounts:login")
def profile_view(request):
    return render(request, "accounts/profile.html")


@login_required(login_url="accounts:login")
def profile_edit_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("accounts:profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "accounts/profile_edit.html", {"form": form})


# ------------------- GESTIÓN DE ROLES (SOLO ADMIN) -------------------
from .models import Role, Profile, Permission


@login_required(login_url="accounts:login")
@role_required(["ADMIN"])
def manage_roles_view(request):
    profiles = Profile.objects.select_related("user", "role")
    roles = Role.objects.prefetch_related("permissions").all()

    # Determinar si se está editando un rol específico
    selected_role_id = request.GET.get("role_id") or request.POST.get("role_id")
    selected_role = None
    if selected_role_id:
        try:
            selected_role = Role.objects.get(id=int(selected_role_id))
        except (Role.DoesNotExist, ValueError):
            selected_role = None

    # Manejo de acciones POST
    if request.method == "POST":
        # 1) Crear/Editar rol
        if "save_role" in request.POST:
            form = RoleForm(request.POST, instance=selected_role)
            if form.is_valid():
                form.save()
                return redirect("accounts:manage_roles")
        # 2) Eliminar rol
        elif "delete_role" in request.POST:
            if selected_role:
                selected_role.delete()
            return redirect("accounts:manage_roles")
        # 3) Asignar roles a usuarios
        elif "assign_roles" in request.POST:
            for profile in profiles:
                role_id = request.POST.get(f"role_{profile.id}")
                if role_id:
                    try:
                        profile.role_id = int(role_id)
                    except ValueError:
                        profile.role = None
                else:
                    profile.role = None
                profile.save()
            return redirect("accounts:manage_roles")

        # Si hay errores de formulario, continuar a render con errores
        form = RoleForm(request.POST, instance=selected_role)
    else:
        # GET: cargar formulario (crear o editar)
        form = RoleForm(instance=selected_role)

    return render(request, "accounts/manage_roles.html", {
        "profiles": profiles,
        "roles": roles,
        "form": form,
        "selected_role": selected_role,
    })
    
    
    
@login_required(login_url="accounts:login")
@role_required(['ADMIN'])
def roles_list_view(request):
    roles = Role.objects.all()
    return render(request, "accounts/roles_list.html", {"roles": roles})


@login_required(login_url="accounts:login")
@role_required(['ADMIN'])
def role_create_view(request):
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description", "")
        if name:
            Role.objects.create(name=name, description=description)
            return redirect("accounts:roles_list")
    return render(request, "accounts/role_form.html", {"action": "Crear"})


@login_required(login_url="accounts:login")
@role_required(['ADMIN'])
def role_edit_view(request, role_id):
    role = Role.objects.get(id=role_id)

    if request.method == "POST":
        role.name = request.POST.get("name")
        role.description = request.POST.get("description", "")
        role.save()
        return redirect("accounts:roles_list")

    return render(request, "accounts/role_form.html", {"role": role, "action": "Editar"})


@login_required(login_url="accounts:login")
@role_required(['ADMIN'])
def role_delete_view(request, role_id):
    role = Role.objects.get(id=role_id)
    if request.method == "POST":
        role.delete()
        return redirect("accounts:roles_list")
    return render(request, "accounts/role_delete.html", {"role": role})

