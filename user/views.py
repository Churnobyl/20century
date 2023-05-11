from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.serializers import UserSerializer, FollowSerializer, UserPointSerializer
from rest_framework.generics import get_object_or_404
from user.models import User
from django.http import HttpResponseRedirect
from rest_framework.permissions import AllowAny
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from dj_rest_auth.registration.views import RegisterView
from rest_framework import permissions
from user.serializers import UserSerializer

class CustomRegisterView(RegisterView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
    


class ConfirmEmailView(APIView):
    permission_classes = [AllowAny]

    def get(self, *args, **kwargs):
        self.object = confirmation = self.get_object()
        confirmation.confirm(self.request)
        # A React Router Route will handle the failure scenario
        return HttpResponseRedirect('/') # 인증성공

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
                return HttpResponseRedirect('/') # 인증실패
        return email_confirmation

    def get_queryset(self):
        qs = EmailConfirmation.objects.all_valid()
        qs = qs.select_related("email_address__user")
        return qs
 
 
class UserDetailView(APIView):
    def get(self, request, user_id):
        user = User.objects.get(id=user_id)
        return Response('my page')
    
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
            serialize = UserSerializer(user, data=request.data)
            if serialize.is_valid():
                serialize.save()
            return Response({'message':'수정완료'}, status=status.HTTP_200_OK)
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