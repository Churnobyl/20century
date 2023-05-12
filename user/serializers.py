from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from user.models import User
from dj_rest_auth.registration.serializers import RegisterSerializer


class UserSerializer(RegisterSerializer, serializers.ModelSerializer):

    profile_image = serializers.ImageField()

    class Meta:
        model = User
        fields = [
            'email',
            'profile_image',
            'password1',
            'password2',
        ]
        # exclude = ['point', 'followings', ]
        extra_kwargs = {
            "password": {
                "write_only": True,
            },
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password')
        instance.set_password(password)
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance

    def custom_signup(self, request, user: User):
        for field in self.Meta.fields:
            if hasattr(user, field) and not getattr(user, field):
                setattr(user, field, self.initial_data[field])

        user.save()


class UserPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['point',]


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'profile_image',]

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        instance.profile_image = validated_data.get(
            "profile_image", instance.profile_image)
        instance.save()
        return instance


class UserDetailDetailSerializer(RegisterSerializer, serializers.ModelSerializer):

    profile_image = serializers.ImageField()

    class Meta:
        model = User
        fields = '__all__'
        # exclude = ['point', 'followings', ]
        extra_kwargs = {
            "password": {
                "write_only": True,
            },
        }


class FollowSerializer(serializers.ModelSerializer):
    followers = serializers.StringRelatedField(many=True)
    followings = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = [
            'followings',
            'followers'
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['username'] = user.username
        token['point'] = user.point

        return token
