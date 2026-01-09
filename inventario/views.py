from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def inventario_home(request):
    return render(request, "inventario/home.html")


