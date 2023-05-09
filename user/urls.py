from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from user import views


#추가하기
urlpatterns = [
    path('', views.UserSignup.as_view(), name='sign_up'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('<int:user_id>/follow/', views.FollowView.as_view(), name='follow'),
    path('<int:user_id>/', views.UserDetailView.as_view(), name='sign_up'),
]
