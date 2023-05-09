from rest_framework import serializers
from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['point',]
        extra_kwargs = {
            "password":{
                "write_only":True,
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
    

class UserPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['point',]


class FollowSerializer(serializers.ModelSerializer):
    followers = serializers.StringRelatedField(many=True)
    followings = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = [
            'followings',
            'followers'
        ]