# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django import forms

from .models import Profile
from .forms import ProfileForm
from .decorators import role_required


# ------------------- FORMULARIO DE REGISTRO -------------------
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None

        # Agregar clases Bootstrap
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
            Profile.objects.get_or_create(user=user)  # Crear perfil automáticamente
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
            request.session['login_error'] = "Usuario o contraseña incorrectos"
            return redirect("accounts:login")

    login_error = request.session.pop('login_error', None)
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
@login_required(login_url="accounts:login")
@role_required(['ADMIN'])
def manage_roles_view(request):
    users = Profile.objects.select_related('user').all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        profile = Profile.objects.get(user_id=user_id)
        profile.role = new_role
        profile.save()
        return redirect('accounts:manage_roles')

    return render(request, 'accounts/manage_roles.html', {'users': users})
