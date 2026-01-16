from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

class CustomUser(AbstractUser):
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True, default='profile_pics/default_img.jpg')
    phone_number = models.CharField(max_length=15, validators=[RegexValidator(r'^\+?\d{10,15}$')], blank=True)

    def __str__(self):
        return self.username