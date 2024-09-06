from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserSignupSerializer(serializers.ModelSerializer):
    tags = serializers.CharField(required=False, allow_blank=True)  # Handle tags as a single string
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    profileImage = serializers.URLField(required=False, allow_blank=True)  # Ensure profileImage is optional

    class Meta:
        model = User
        fields = ['id', 'username', 'firstName', 'middleName', 'lastName', 'email', 'phone', 'password', 'profileImage', 'tags', 'bio', 'followers', 'following']

    def create(self, validated_data):
        tags_data = validated_data.pop('tags', '')
        password = validated_data.pop('password', None)

        # Set default value for profileImage if not provided
        if 'profileImage' not in validated_data:
            validated_data['profileImage'] = 'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/1.png'

        # Hash the password before saving
        if password:
            validated_data['password'] = make_password(password)

        # Create the user instance
        user = User.objects.create(**validated_data)

        # Handle tags as a comma-separated string
        user.tags = tags_data
        user.save()

        return user
        
    def get_followers(self, obj):
        return [user.username for user in obj.followers.all()]

    def get_following(self, obj):
        return [user.username for user in obj.following.all()]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'firstName', 'middleName', 'lastName', 'email', 'phone', 'profileImage', 'tags', 'bio', 'followers', 'following']
