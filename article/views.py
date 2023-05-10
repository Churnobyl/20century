from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from article.models import Article, Comment, Product, Bid
from article.serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    ArticleCreateSerializer,
    ArticleUpdateSerializer,
    CommentSerializer,
    ProductSerializer,
    BidCreateSerializer
)
from article.serializers import BookmarkSerializer
from rest_framework.pagination import PageNumberPagination

class ArticlePagination(PageNumberPagination):
    page_size = 6


class ArticleView(APIView):
    pagination_class = ArticlePagination
    serializer_class = ArticleListSerializer
    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        else:
            pass
        return self._paginator
    
    def paginate_queryset(self, queryset):
        
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset,
                   self.request, view=self)
        
    def get_paginated_response(self, data):
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)
    
    def get(self, request):
        articles = Article.objects.all().order_by('-created_at')
        page = self.paginate_queryset(articles)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        article_serializer = ArticleCreateSerializer(data=request.data)
        product_serializer = ProductSerializer(data=request.data)
        bid_serializer = BidCreateSerializer(data=request.data)
        if article_serializer.is_valid() and product_serializer.is_valid() and bid_serializer.is_valid():
            article_serializer.save(user=request.user)
            product_serializer.save()
            bid_serializer.save()
            return Response({'article': article_serializer.data, 'product': product_serializer.data, 'bid': bid_serializer.data}, status=status.HTTP_200_OK)
        else:
            errors = {}
            errors.update(article_serializer.errors)
            errors.update(product_serializer.errors)
            errors.update(bid_serializer.errors)
            return Response(errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class ArticleDetailView(APIView):
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            serializer = ArticleSerializer(article)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    def patch(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            serializer = ArticleUpdateSerializer(article, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)
        
        
class BookmarkView(APIView):
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        serializer = BookmarkSerializer(article)
        return Response(serializer.data)
    
    def post(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user in article.bookmarked.all():
            article.bookmarked.remove(request.user)
            return Response({"message": "북마크에서 삭제했습니다."}, status=status.HTTP_202_ACCEPTED)
        else:
            article.bookmarked.add(request.user)
            return Response({"message": "북마크에 추가했습니다."}, status=status.HTTP_200_OK)
        

class CommentView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 댓글 작성
    def post(self, request, article_id):
        serializer = CommentSerializer(data=request.data)
        article = Article.objects.get(id=article_id)
        if serializer.is_valid():
            serializer.save(user=request.user, article=article)
            return Response({'message':'댓글 작성 완료'}, status=status.HTTP_201_CREATED)
        else:    
            return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class CommentDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    # 댓글 수정
    def put(self, request, article_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id, article_id=article_id)
        article = Article.objects.get(id=article_id)
        if request.user == comment.user:
            serializer = CommentSerializer(comment, data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, article=article)
                return Response({'message':'댓글 수정 완료'}, status=status.HTTP_200_OK)
            else:    
                return Response({'error':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error':'권한이 없습니다!'}, status=status.HTTP_401_UNAUTHORIZED)

    # 댓글 삭제
    def delete(self, request, article_id, comment_id):
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user == comment.user:
            comment.delete()
            return Response({'message':'댓글 삭제 완료'}, status=status.HTTP_200_OK)
        else:
            return Response({'error':'권한이 없습니다!'}, status=status.HTTP_401_UNAUTHORIZED)