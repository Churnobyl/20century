from django.contrib import admin
from django.urls import path, include, re_path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from dj_rest_auth.registration.views import VerifyEmailView
from user import views
from user.views import ConfirmEmailView
from django.conf import settings
from django.conf.urls.static import static



#추가하기
urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('<int:user_id>/follow/', views.FollowView.as_view(), name='follow'),
    path('<int:user_id>/', views.UserDetailView.as_view(), name='sign_up'),
    # 비번 변경
    # http://127.0.0.1:8000/api/user/account/password_reset/
    path('account/', include('django.contrib.auth.urls')),
    # 일반 회원 회원가입/로그인
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    # 유효한 이메일이 유저에게 전달
    re_path(r'^account-confirm-email/$', VerifyEmailView.as_view(), name='account_email_verification_sent'),
    # 유저가 클릭한 이메일(=링크) 확인
    re_path(r'^account-confirm-email/(?P<key>[-:\w]+)/$', ConfirmEmailView.as_view(), name='account_confirm_email'),
]

urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)

# api/user/ dj-rest-auth/ password/reset/ [name='rest_password_reset']
# api/user/ dj-rest-auth/ password/reset/confirm/ [name='rest_password_reset_confirm']
# api/user/ dj-rest-auth/ login/ [name='rest_login']
# api/user/ dj-rest-auth/ logout/ [name='rest_logout']
# api/user/ dj-rest-auth/ user/ [name='rest_user_details']
# api/user/ dj-rest-auth/ password/change/ [name='rest_password_change']
# api/user/ dj-rest-auth/registration/
