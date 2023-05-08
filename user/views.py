from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from user.serializers import UserSerializer

class UserSignup(APIView):
    def post(self, request):
        serialize = UserSerializer(data=request.data)
        if serialize.is_valid():
            serialize.save()
            return Response({'message': '가입완료'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'errors':f'${serialize.errors}'}, status=status.HTTP_400_BAD_REQUEST)