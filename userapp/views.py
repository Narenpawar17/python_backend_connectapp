from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse
from userapp.models import User
from userapp.serializers import UserSignupSerializer, UserLoginSerializer,UserSerializer
from userapp.utils import custom_response
from userapp.utils import decode_token
import cloudinary.uploader # type: ignore


# for checking backend running or not 
def checkup(request):
    return JsonResponse({"message": "Backend is running successfully"})


# User signup view
class SignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return custom_response(True, data=UserSignupSerializer(user).data, status_code=status.HTTP_201_CREATED)
        return custom_response(False, error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


# User login view with jwt verification
class LoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(email=email)
                if check_password(password, user.password):  
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)

                    data = {
                        'access': access_token,
                        'refresh': refresh_token,
                        'email': user.email,
                        'username': user.username,
                    }
                    return custom_response(True, data=data, status_code=status.HTTP_200_OK)
                else:
                    return custom_response(False, error='Password Incorrect!', status_code=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return custom_response(False, error='User not found!', status_code=status.HTTP_404_NOT_FOUND)
        
        return custom_response(False, error=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)
    

# User list view with JWT verification
class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer

    def get(self, request):
        # Decode the JWT token
        payload = decode_token(request)
        
        # check the token ki yeh valid hai ki nhi 
        if payload is None:
            return custom_response(False, error='Invalid or missing token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # fetching the userlist
        queryset = User.objects.all()
        serializer = self.get_serializer(queryset, many=True)
        return custom_response(True, data={'users': serializer.data, 'payload': payload}, status_code=status.HTTP_200_OK)


# user by username view with jwt verification
class UserByUsername(APIView):
    def get(self, request, username):
        # print(username)
        payload = decode_token(request)
        # print("Payload : ",payload)
        if payload is None:
            return custom_response(False, error='Invalid or missing token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        # print("username is : ", username)
        try:
            user = User.objects.get(username=username)
            serializer = UserSerializer(user)
            return custom_response(True, data={'user': serializer.data, 'payload': payload}, status_code=status.HTTP_200_OK)
        except User.DoesNotExist:
            return custom_response(False, error=f'User not found. Payload: {payload}', status_code=status.HTTP_404_NOT_FOUND)


# Delete user view
class DeleteUserView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, username):
        try:
            user = get_object_or_404(User, username=username)
            user.delete()
            return custom_response(True, data=None, status_code=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return custom_response(False, error=f"User '{username}' not found", status_code=status.HTTP_404_NOT_FOUND)


# Current User profile view with jwt verification
class CurrentUserProfileView(APIView):
    def get(self, request):
        # decoding jwt token
        payload = decode_token(request)
        
  
        if payload is None:
            return custom_response(False, error='Invalid or missing token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Get the current user using the user_id from the token payload
            user = User.objects.get(id=payload['user_id'])
            serializer = UserSerializer(user)
            return custom_response(True, data={'user': serializer.data, 'payload': payload}, status_code=status.HTTP_200_OK)
        except User.DoesNotExist:
            return custom_response(False, error='User not found', status_code=status.HTTP_404_NOT_FOUND)


# Update email view for current user with jwt verification
class UpdateUserEmailView(APIView):
    def put(self, request):
        # Decode the JWT token
        payload = decode_token(request)
        
        # Check if the token is valid
        if payload is None:
            return custom_response(False, error='Invalid or missing token', status_code=status.HTTP_401_UNAUTHORIZED)

        try:
            # Get the current user using the user_id from the token payload
            user = User.objects.get(id=payload['user_id'])
            new_email = request.data.get('email')

            if not new_email:
                return custom_response(False, error='Email is required', status_code=status.HTTP_400_BAD_REQUEST)

            # Check if the email is already in use
            if User.objects.filter(email=new_email).exists():
                return custom_response(False, error='Email is already taken', status_code=status.HTTP_400_BAD_REQUEST)

            # Update the user's email
            user.email = new_email
            user.save()

            # Serialize the updated user and return the response
            serializer = UserSerializer(user)
            return custom_response(True, data=serializer.data, status_code=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return custom_response(False, error='User not found', status_code=status.HTTP_404_NOT_FOUND)


# Update password view for the current user with jwt verification
class UpdateUserPasswordView(APIView):
    def put(self, request):
        # Decode the JWT token
        payload = decode_token(request)
        
        # Check if the token is valid
        if payload is None:
            return custom_response(False, error='Invalid or missing token', status_code=status.HTTP_401_UNAUTHORIZED)

        try:
            # Get the current user using the user_id from the token payload
            user = User.objects.get(id=payload['user_id'])
            
            current_password = request.data.get('current_password')
            new_password = request.data.get('new_password')

            if not current_password or not new_password:
                return custom_response(False, error='Current and new passwords are required', status_code=status.HTTP_400_BAD_REQUEST)

            # Check if the current password is correct
            if not check_password(current_password, user.password):
                return custom_response(False, error='Current password is incorrect', status_code=status.HTTP_400_BAD_REQUEST)

            # Update the user's password (after hashing it)
            user.password = make_password(new_password)
            user.save()

            return custom_response(True, data='Password updated successfully', status_code=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return custom_response(False, error='User not found', status_code=status.HTTP_404_NOT_FOUND)


# Update bio and tag for the current user with jwt verification
class UpdateUserProfileView(APIView):
    def put(self, request, username):

        payload = decode_token(request)
        
        if payload is None:
            return custom_response(False, error='Invalid or missing token', status_code=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Get the user by username
            user = User.objects.get(username=username)
            
            # Ensure that the user updating the profile is allowed to or not
            if user.id != payload['user_id']:
                return custom_response(False, error='You are not authorized to update this profile', status_code=status.HTTP_403_FORBIDDEN)
            
            bio = request.data.get('bio')
            tags_data = request.data.get('tags', '')

            # Update the bio if provided
            if bio is not None:
                user.bio = bio

            # Update tags if provided
            if tags_data:
                # Store tags as a comma-separated string
                user.tags = ','.join(tag.strip() for tag in tags_data.split(','))
            
            # Save the updated user profile
            user.save()

            # Serialize the updated user profile
            serializer = UserSerializer(user)

            return custom_response(True, data=serializer.data, status_code=status.HTTP_200_OK)

        except User.DoesNotExist:
            return custom_response(False, error='User not found', status_code=status.HTTP_404_NOT_FOUND)


# profile picture uploading using cloudinary
class UploadProfilePictureView(APIView):
    def post(self, request):
        # Decode the JWT token
        payload = decode_token(request)
        
        # Check if the token is valid
        if payload is None:
            return custom_response(False, error='Invalid or missing token', status_code=status.HTTP_401_UNAUTHORIZED)

        try:
            # Get the current user from the token payload
            user = User.objects.get(id=payload['user_id'])

            # Retrieve the uploaded file
            file = request.FILES.get('profileImage')

            if not file:
                return custom_response(False, error='No file uploaded', status_code=status.HTTP_400_BAD_REQUEST)

            # Upload the file to Cloudinary
            upload_result = cloudinary.uploader.upload(file)
            profile_image_url = upload_result['url']

            # Update the user's profile image
            user.profileImage = profile_image_url
            user.save()

            return custom_response(True, data={'profileImage': user.profileImage}, status_code=status.HTTP_200_OK)

        except User.DoesNotExist:
            return custom_response(False, error='User not found', status_code=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print(f'Error uploading profile picture: {e}')
            return custom_response(False, error='Error uploading profile picture', status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# follow user view with jwt implementation
class FollowUserView(APIView):
    def post(self, request):
        payload = decode_token(request)

        if payload is None:
            return custom_response(False, error='Invalid or missing token', status_code=status.HTTP_401_UNAUTHORIZED)

        current_user_id = payload['user_id']
        user_to_follow_id = request.data.get('userId')

        if not user_to_follow_id:
            return custom_response(False, error='userId is required', status_code=status.HTTP_400_BAD_REQUEST)

        if not User.objects.filter(id=user_to_follow_id).exists():
            return custom_response(False, error='User to follow not found', status_code=status.HTTP_404_NOT_FOUND)

        current_user = get_object_or_404(User, id=current_user_id)
        user_to_follow = get_object_or_404(User, id=user_to_follow_id)

        if user_to_follow in current_user.following.all():
            return custom_response(False, error='Already following this user', status_code=status.HTTP_400_BAD_REQUEST)

        # Update following and followers lists
        current_user.following.add(user_to_follow)
        current_user.followingCount += 1
        current_user.save()

        user_to_follow.followers.add(current_user)
        user_to_follow.followersCount += 1
        user_to_follow.save()

        return custom_response(
            True,
            data={
                'message': 'Followed successfully',
                'userId': user_to_follow_id,
                'followersCount': user_to_follow.followersCount,
                'followingCount': current_user.followingCount,
            },
            status_code=status.HTTP_200_OK
        )


# Unfollow user view with jwt implementation
class UnfollowUserView(APIView):
    def post(self, request):
        payload = decode_token(request)
        
        if payload is None:
            return Response({'success': False, 'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user_id = request.data.get('userId')
        current_user_id = payload['user_id']

        try:
            # Validate userId
            user_to_unfollow = get_object_or_404(User, id=user_id)
            current_user = get_object_or_404(User, id=current_user_id)

            # Get the list of IDs that the current user is following
            following_ids = current_user.following.values_list('id', flat=True)

            # Check if the current user is not following the target user
            if user_to_unfollow.id not in following_ids:
                return Response({'success': False, 'error': 'Not following this user'}, status=status.HTTP_400_BAD_REQUEST)

            # Update both users' following and followers lists
            current_user.following.remove(user_to_unfollow)
            current_user.followingCount -= 1
            current_user.save()

            user_to_unfollow.followers.remove(current_user)
            user_to_unfollow.followersCount -= 1
            user_to_unfollow.save()

            return Response({
                'success': True,
                'message': 'Unfollowed successfully',
                'userId': user_id,
                'followersCount': user_to_unfollow.followersCount,
                'followingCount': current_user.followingCount,
            }, status=status.HTTP_200_OK)

        except Exception as e:
            print(f"Error unfollowing user: {e}")
            return Response({'success': False, 'error': 'Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Search User by tag view with jwt implemented
class SearchUsersByTagView(APIView):
    def get(self, request, tag):
        # Decode the JWT token
        payload = decode_token(request)
        if payload is None:
            return Response({'success': False, 'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)

        print('Received tag:', tag)

        if not tag:
            return Response({'message': 'Tag is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            users = User.objects.filter(tags__icontains=tag)

            if not users.exists():
                return Response({'message': 'No users found with this tag'}, status=status.HTTP_404_NOT_FOUND)

            user_data = []
            for user in users:
                user_data.append({
                    'id': user.id,
                    'username': user.username,
                    'profileImage': user.profileImage.url if user.profileImage else None,
                    'followersCount': user.followersCount,
                    'followingCount': user.followingCount,
                    'bio': user.bio,
                })

            return Response(user_data, status=status.HTTP_200_OK)

        except Exception as error:
            print('Error searching users by tag:', error)
            return Response({'message': 'Server error', 'error': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
































