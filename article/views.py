from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from article.models import Article, Comment
from article.serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    ArticleCreateSerializer,
    ArticleUpdateSerializer,
    CommentSerializer,
)
from article.serializers import BookmarkSerializer
from rest_framework.generics import ListAPIView


class ArticleView(APIView):
    def get(self, request):
        articles = Article.objects.all().order_by('-created_at')
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = ArticleCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class ArticleDetailView(APIView):
    def get(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            serializer = ArticleSerializer(article)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)

    def put(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if request.user == article.user:
            serializer = ArticleUpdateSerializer(article, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("권한이 없습니다.", status=status.HTTP_403_FORBIDDEN)
        
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