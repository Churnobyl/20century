from rest_framework import serializers
from article.models import Article, Comment, Bid


class ArticleSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    image = serializers.ImageField()

    def get_user(self, obj):
        return obj.user.username

    class Meta:
        model = Article
        fields = [
            'id',
            'user',
            'title',
            'content',
            'created_at',
            'updated_at',
            'finished_at',
            'category',
            'product',
            'progress',
            'max_user',
            'max_point',
            'image',
            'bookmarked',
            'user_id',
        ]


class ArticleCreateSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Article
        fields = ["title", "content", "finished_at",
                  "category", "product", "image", "max_point"]


class ArticleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["product", "category", "content"]


class ArticleListSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return obj.user.username

    class Meta:
        model = Article
        fields = ["title", "user", "finished_at", "product",
                  'progress', "max_point", "id", "image", 'bookmarked',]


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
        fields = "__all__"


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["content",]
