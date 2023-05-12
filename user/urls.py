from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from dj_rest_auth.registration.views import VerifyEmailView
from user import views
from user.views import ConfirmEmailView



#추가하기
urlpatterns = [
    path('<int:user_id>/follow/', views.FollowView.as_view(), name='follow'),
    path('<int:user_id>/', views.UserDetailView.as_view(), name='sign_up'),
    # 로그인 토큰 커스텀
    path('api/token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 비번 변경
    # http://127.0.0.1:8000/api/user/account/password_reset/
    path('account/', include('django.contrib.auth.urls')),
    # 일반 회원 회원가입/로그인
    path('dj-rest-auth/registration/', views.CustomRegisterView.as_view(), name='register'),
    # 유효한 이메일이 유저에게 전달
    re_path(r'^account-confirm-email/$', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    # 유저가 클릭한 이메일(=링크) 확인
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(), name='account_confirm_email'),
]



# api/user/ dj-rest-auth/ password/reset/ [name='rest_password_reset']
# api/user/ dj-rest-auth/ password/reset/confirm/ [name='rest_password_reset_confirm']
# api/user/ dj-rest-auth/ login/ [name='rest_login']
# api/user/ dj-rest-auth/ logout/ [name='rest_logout']
# api/user/ dj-rest-auth/ user/ [name='rest_user_details']
# api/user/ dj-rest-auth/ password/change/ [name='rest_password_change']
# api/user/ dj-rest-auth/registration/
