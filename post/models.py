from django.db import models
from userapp.models import User  

class Post(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=25)
    imgUrl = models.URLField(max_length=500)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    archived = models.BooleanField(default=False)

    def __str__(self):
        return self.name
