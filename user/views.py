from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from article.models import Article, Bid
from article.serializers import ArticleSerializer, BiddingSerializer, BiddingArticleSerializer
from user.serializers import UserSerializer, FollowSerializer, UserPointSerializer, CustomTokenObtainPairSerializer
from rest_framework.generics import get_object_or_404
from user.models import User
from django.http import HttpResponseRedirect
from rest_framework.permissions import AllowAny
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from rest_framework_simplejwt.views import TokenObtainPairView
from dj_rest_auth.registration.views import RegisterView
from rest_framework import permissions
from user.serializers import UserSerializer, UserDetailSerializer, UserDetailDetailSerializer
from rest_framework.parsers import MultiPartParser
# 카카오
import os
import requests
from django.shortcuts import redirect
from django.http import JsonResponse
from json import JSONDecodeError
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.kakao import views as kakao_view
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

class CustomRegisterView(RegisterView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    


class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        # A React Router Route will handle the failure scenario
        return HttpResponseRedirect('http://127.0.0.1:5500') # 인증성공

    def get_object(self, queryset=None):
        key = self.kwargs['key']
        email_confirmation = EmailConfirmationHMAC.from_key(key)
        if not email_confirmation:
            if queryset is None:
                queryset = self.get_queryset()
            try:
                email_confirmation = queryset.get(key=key.lower())
            except EmailConfirmation.DoesNotExist:
                # A React Router Route will handle the failure scenario
                return HttpResponseRedirect('http://127.0.0.1:5500') # 인증실패
        return email_confirmation
 
    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs
    

# 카카오 로그인
BASE_URL = 'http://127.0.0.1:8000/'
KAKAO_CALLBACK_URI = BASE_URL + 'api/user/kakao/callback/'

def kakao_login(request):
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")
    return redirect(f"https://kauth.kakao.com/oauth/authorize?client_id={client_id}&redirect_uri={KAKAO_CALLBACK_URI}&response_type=code&scope=account_email")

def kakao_callback(request):
    code = request.GET.get("code")
    token_api = 'https://kauth.kakao.com/oauth/token'
    client_id = os.environ.get("SOCIAL_AUTH_KAKAO_CLIENT_ID")

    data = {
        'grant_type' : 'authorization_code',
        'client_id' : client_id,
        'redirection_uri': KAKAO_CALLBACK_URI,
        'code': code,
    }

    token_response = requests.post(token_api, data=data)
    access_token = token_response.json().get('access_token')

    user_request = requests.post('https://kapi.kakao.com/v2/user/me', headers={"Authorization": f'Bearer ${access_token}'})
    user_json = user_request.json()


    return JsonResponse({"Id token": user_json["id"],"Code": data["client_id"], 'Access token':access_token})


class KakaoLogin(SocialLoginView):
    adapter_class = kakao_view.KakaoOAuth2Adapter
    callback_url = KAKAO_CALLBACK_URI
    client_class = OAuth2Client
 
 
class UserDetailView(APIView):
    # 유저 정보 조회
    def get(self, request, user_id=None):
        # 내 정보 가져오기
        user = User.objects.get(id=user_id)
        user_serializer = UserDetailDetailSerializer(user)

        # 입찰웨않뒈?
        bids = Bid.objects.filter(max_user=user_id)
        bid_serializer = BiddingArticleSerializer(bids, many=True)
            
        
        # 찜 목록 : 최신순 (id)
        # 북마크 DB의 user_id를 조회해서
        # article_id 가져와야함
        
        users_bookmark = user.bookmark.all()
        book_serializer = ArticleSerializer(users_bookmark, many=True)
        

        return Response({'user':user_serializer.data, 'book':book_serializer.data, 'bid_article': bid_serializer.data},status=status.HTTP_200_OK)
    
    # 회원 포인트 충전
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        login = request.user
        
        if login==user:
            serialize = UserPointSerializer(user, data={'point': request.data['point'] + user.point})
            if serialize.is_valid():
                serialize.save()
                return Response({'message':'충전완료'}, status=status.HTTP_200_OK)
        else:
            return Response({'error':'권한이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    # 회원정보 수정
    def put(self, request, user_id):      
        user = get_object_or_404(User, id=user_id)
        login = request.user
        if login==user:
            serialize = UserDetailSerializer(user, data=request.data)
            if serialize.is_valid():
                serialize.save()
                return Response(serialize.data, status=status.HTTP_200_OK)
            else:
                return Response(serialize.errors)
        else:
            return Response({'error':'권한이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)

    # 회원탈퇴 (is_active=False)
    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        login = request.user
        
        if login==user:
            request.user.is_active = False
            request.user.save()
            return Response({'message':'회원탈퇴'}, status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION)
        else:
            return Response({'error':'권한이 없습니다.'}, status=status.HTTP_400_BAD_REQUEST)
        
class FollowView(APIView):
    def get(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        serializer = FollowSerializer(you)
        return Response(serializer.data)
    
    def post(self, request, user_id):
        you = get_object_or_404(User, id=user_id)
        me = request.user
        if me in you.followers.all():
            you.followers.remove(me)
            return Response("unfollow했습니다.", status=status.HTTP_200_OK)
        else:
            you.followers.add(me)
            return Response("follow했습니다.", status=status.HTTP_200_OK)
        
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer