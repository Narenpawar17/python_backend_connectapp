from django.db import models
from cloudinary.models import CloudinaryField # type: ignore


class User(models.Model):
    firstName = models.CharField(max_length=255, blank=False)
    middleName = models.CharField(max_length=255, blank=True, null=True)
    lastName = models.CharField(max_length=255, blank=False)
    username = models.CharField(max_length=255, unique=True, blank=False)
    email = models.EmailField(unique=True, blank=False)
    phone = models.CharField(max_length=15, unique=True, blank=False)
    password = models.CharField(max_length=255, blank=False)
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following')
    postsCount = models.IntegerField(default=0)
    followersCount = models.IntegerField(default=0)
    followingCount = models.IntegerField(default=0)
    profileImage = CloudinaryField(default='https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png')
    # profileImage = CloudinaryField('profileImage', blank = True, null = True)
    tags = models.CharField(max_length=255, blank=True)  
    bio = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.username
