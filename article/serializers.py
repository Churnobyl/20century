from rest_framework import serializers
from article.models import Article, Comment, Bid


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.username

    class Meta:
        model = Article
        fields = "__all__"


class ArticleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["title", "content", "finished_at", "category", "product"]


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
        fields = ["title", "user", "finished_at", "product"]


# class ProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = "__all__"


# class ProductUpdateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Product
#         fields = ["progress"]


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
