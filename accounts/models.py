# accounts/models.py
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('MANAGER', 'Gestor'),
        ('USER', 'Usuario'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        upload_to='profiles/',
        default='profiles/default.png',
        blank=True
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='USER')

    def __str__(self):
        return f"{self.user.username} ({self.role})"
