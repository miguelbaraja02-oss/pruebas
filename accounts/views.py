from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django import forms

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].help_text = None
        self.fields['password1'].help_text = None
        self.fields['password2'].help_text = None
        
        # Agregar clases Bootstrap a los campos
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        # Guardar el email proporcionado en el formulario
        user.email = self.cleaned_data.get('email')
        if commit:
            user.save()
        return user

def login_view(request):
    login_error = None

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("welcome")
        else:
            request.session['login_error'] = "Usuario o contraseña incorrectos"
            return redirect("login")
    else:
        # Obtener el error de la sesión si existe
        login_error = request.session.pop('login_error', None)

    # Renderizar y asegurar que el navegador no use una versión cacheada del formulario
    response = render(request, "accounts/login.html", {"login_error": login_error})
    response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

def register_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required(login_url="login")
def home(request):
    return render(request, "accounts/home.html")


@login_required(login_url='login')
def welcome_view(request):
    return render(request, 'accounts/welcome.html')

