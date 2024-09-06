# In post/serializers.py
from rest_framework import serializers
from .models import Post

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'name', 'address', 'phone', 'imgUrl', 'owner', 'archived']
