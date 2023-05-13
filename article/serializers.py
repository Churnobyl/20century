from rest_framework import serializers
from article.models import Article, Comment, Bid


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

    class Meta:
        model = Article
        fields = ["title", "content", "finished_at",
                  "category", "product", "image"]


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


class CloseAuctionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = ["progress"]


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


class BiddingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bid
        fields = ["user", "max_point"]


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
