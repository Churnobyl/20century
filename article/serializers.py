from rest_framework import serializers
from article.models import Article, Comment, Bid
from django.utils import timezone


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    image = serializers.ImageField()

    def get_user(self, obj):
        return obj.user.username

    class Meta:
        model = Article
        fields = "__all__"


class ArticleCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()
    finished_at = serializers.DateTimeField()

    class Meta:
        model = Article
        fields = ["title", "content", "finished_at",
                  "category", 'image', 'name']


class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["title", "content", "category"]


class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.username

    class Meta:
        model = Article
        fields = ["pk", "title", "user", "finished_at"]


class BidCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = "__all__"


class BookmarkSerializer(serializers.ModelSerializer):
    bookmarked = serializers.StringRelatedField(many=True)

    class Meta:
        model = Article
        fields = [
            'bookmarked',
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content",]


class BiddingSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    class Meta:
        model = Bid
        fields = ['user', 'max_point']
