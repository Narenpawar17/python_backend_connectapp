# In post/urls.py
from django.urls import path
from .views import CreatePostView, UpdatePostView, GetPostsByOwnerEmailView, GetPostsByUsernameView
from .views import DeletePostView, ArchivePostView, GetArchivedPostsByOwnerEmailView

urlpatterns = [
    path('posts/create/', CreatePostView.as_view(), name='create_post'),
    path('posts/<int:id>/', UpdatePostView.as_view(), name='update_post'),
    path('posts/delete/<int:id>/', DeletePostView.as_view(), name='delete-post'),
    path('posts/owner/<str:email>/', GetPostsByOwnerEmailView.as_view(), name='get_posts_by_owner_email'),
    path('posts/archive/<int:id>/', ArchivePostView.as_view(), name='archive-post'),
    path('posts/archived/owner/<str:email>/', GetArchivedPostsByOwnerEmailView.as_view(), name='archived-posts-by-owner-email'),
]
