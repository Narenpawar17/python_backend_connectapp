from django.urls import path
from .views import checkup
from .views import SignupView, LoginView
from .views import UserListView, UserByUsername, DeleteUserView, CurrentUserProfileView
from .views import UpdateUserEmailView, UpdateUserPasswordView, UpdateUserProfileView
from .views import UploadProfilePictureView, FollowUserView, UnfollowUserView, SearchUsersByTagView

urlpatterns = [
    path('checkup/', checkup, name='checkup'),
    path('signup/', SignupView.as_view(), name='signup_user'),
    path('login/', LoginView.as_view(), name='login_user'),
    path('all-users/', UserListView.as_view(), name='user-list'),
    path('user/', CurrentUserProfileView.as_view(), name='current_user_profile'),
    path('user/change-email/', UpdateUserEmailView.as_view(), name='update_user_email'),
    path('user/change-password/', UpdateUserPasswordView.as_view(), name='update_user_password'),
    path('users/uploadProfilePicture/', UploadProfilePictureView.as_view(), name='upload_profile_picture'),
    path('users/follow/', FollowUserView.as_view(), name='follow_user'),
    path('users/unfollow/', UnfollowUserView.as_view(), name='follow_user'),
    path('users/<str:username>/', UserByUsername.as_view(), name='user-by-username'),
    path('delete-user/<str:userName>/', DeleteUserView.as_view(), name='delete-user'),
    path('users/<str:username>/update-biotag/', UpdateUserProfileView.as_view(), name='update_user_profile'),
    path('users/searchtag/<str:tag>/', SearchUsersByTagView.as_view(), name='search_users_by_tag'),
]




