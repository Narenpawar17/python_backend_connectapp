from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Post
from .serializers import PostSerializer
from userapp.models import User 
from userapp.utils import decode_token 
from django.shortcuts import get_object_or_404


# VIEW FOR CREATING A POST BY A USER
class CreatePostView(APIView):
    def post(self, request):
        payload = decode_token(request)
        
        if payload is None:
            return Response({'success': False, 'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # owner koh current user set krdo
        request.data['owner'] = payload['user_id']  

        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            try:
                # user ka post count increase kr denge
                user = User.objects.get(id=payload['user_id'])
                user.postsCount += 1
                user.save()
            except User.DoesNotExist:
                print('User not found')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# VIEW FOR UPDATING A POST 
class UpdatePostView(APIView):
    def put(self, request, id):
        payload = decode_token(request)
        
        if payload is None:
            return Response({'success': False, 'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        post = get_object_or_404(Post, id=id)
        
        # Check if the current user is the owner of the post
        if post.owner.id != payload['user_id']:
            return Response({'success': False, 'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        # Update the post with the new data
        # partial=True allows partial updates
        serializer = PostSerializer(post, data=request.data, partial=True)  
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# VIEW FOR FETCHING ALL THE POST CREATED BY THE USER THROUGH THE EMAIL
class GetPostsByOwnerEmailView(APIView):
    def get(self, request, email):
        # Decode JWT and verify user
        payload = decode_token(request)
        
        if payload is None:
            return Response({'success': False, 'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Print for debugging
            print('Requested Email:', email)
            if not email:
                return Response({'success': False, 'error': 'Email parameter not provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Find the user by email
            user = get_object_or_404(User, email=email)
            
            # Fetch only non-archived posts created by the user
            posts = Post.objects.filter(owner=user, archived=False)
            
            # Serialize the posts data
            serializer = PostSerializer(posts, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as error:
            print('Error fetching posts by owner email:', error)
            return Response({'success': False, 'error': 'Error fetching posts', 'message': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# VIEW FOR FETCHIGN ALL THE POST CREATED BY USER THROUGH THE USERNAME 
class GetPostsByUsernameView(APIView):
    def get(self, request, username):
        # Decode JWT and verify user
        payload = decode_token(request)
        print("payload is " , payload)
        if payload is None:
            return Response({'success': False, 'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # Find the user by username
            user = get_object_or_404(User, username=username)
            
            # Fetch only non-archived posts created by the user
            posts = Post.objects.filter(owner=user, archived=False)
            
            # Serialize the posts data
            serializer = PostSerializer(posts, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as error:
            print('Error fetching posts by username:', error)
            return Response({'success': False, 'error': 'Error fetching posts', 'message': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# VIEW FOR DELETING A POST MADE BY THE USER
class DeletePostView(APIView):
    def delete(self, request, id):
        payload = decode_token(request)
        print("Payload is ", payload)
        
        if payload is None:
            return Response({'success': False, 'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            # finding the post to be deleted
            post = get_object_or_404(Post, id=id)
            
            # check if the logged-in user is the owner of the post
            if post.owner.id != payload['user_id']:
                return Response({'success': False, 'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            
            # delete the post
            post.delete()
            
            # find user and decrement the post count
            user = get_object_or_404(User, id=payload['user_id'])
            user.postsCount = max(0, user.postsCount - 1)  # Decrement post count but ensure it doesn't go negative
            user.save()
            
            return Response({'success': True, 'message': 'Post deleted'}, status=status.HTTP_200_OK)
        
        except Exception as error:
            return Response({'success': False, 'error': 'Error deleting post', 'message': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# VIEW FOR ARCHIVE PAGE, SHOWING ALL THE POST THAT ARE ARCHIVED
class ArchivePostView(APIView):
    def patch(self, request, id):
        payload = decode_token(request)
        print("payload is : ", payload)

        if payload is None:
            return Response({'success': False, 'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Find the post by ID
            post = Post.objects.filter(id=id).first()  # Use filter().first() to avoid `get()` exceptions
            if not post:
                return Response({'message': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Check if the logged-in user is the owner of the post
            if post.owner.id != payload['user_id']:
                return Response({'success': False, 'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
            
            # Update the archived status
            archived = request.data.get('archived')
            print("archive status : ", request.data.get('archived'))
            if archived is None or not isinstance(archived, bool):
                return Response({'message': 'Invalid archived status'}, status=status.HTTP_400_BAD_REQUEST)
            
            post.archived = archived
            post.save()
            
            # Serialize the updated post
            serializer = PostSerializer(post)
            return Response({'message': 'Post updated successfully', 'post': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as error:
            print('Error updating post archive status:', error)
            return Response({'success': False, 'error': 'Error updating post archive status', 'message': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# VIEW FOR FETCHING ARCHIVED POST CREATED BY THE USER
class GetArchivedPostsByOwnerEmailView(APIView):
    def get(self, request, email):
        # Decode JWT and verify user
        payload = decode_token(request)
        
        if payload is None:
            return Response({'success': False, 'error': 'Invalid or missing token'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            # Find the user by email
            user = get_object_or_404(User, email=email)
            
            # Fetch archived posts created by the user
            posts = Post.objects.filter(owner=user, archived=True)
            
            # Serialize the posts data
            serializer = PostSerializer(posts, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as error:
            print('Error fetching archived posts by owner email:', error)
            return Response({'success': False, 'error': 'Error fetching archived posts', 'message': str(error)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)












