from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.serializers import UserSerializer, FollowSerializer
from rest_framework.generics import get_object_or_404
from user.models import User

class UserSignup(APIView):
    def post(self, request):
        serialize = UserSerializer(data=request.data)
        if serialize.is_valid():
            serialize.save()
            return Response({'message': '가입완료'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors':f'${serialize.errors}'}, status=status.HTTP_400_BAD_REQUEST)
        

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