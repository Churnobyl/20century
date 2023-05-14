from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status, permissions
from rest_framework.response import Response
from article.models import Article, Comment, Bid
from article.serializers import (
    ArticleSerializer,
    ArticleListSerializer,
    ArticleCreateSerializer,
    ArticleUpdateSerializer,
    CommentSerializer,
    BookmarkSerializer,
    BidCreateSerializer,
    BiddingSerializer
)
from rest_framework.pagination import PageNumberPagination
import pytz
from datetime import datetime, timedelta
import logging


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
        time_zone = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(time_zone) + timedelta(minutes=32)
        date_format = '%Y-%m-%d %H:%M:%S'
        finished_at = datetime.strptime(request.data['finished_at'], date_format).replace(tzinfo=time_zone)
        if finished_at < current_time:
            return Response({"message":"경매 종료시간은 현재시간 이후로 설정해야 합니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            article_serializer = ArticleCreateSerializer(data=request.data)
            bid_serializer = BidCreateSerializer(data=request.data)
            if article_serializer.is_valid() and bid_serializer.is_valid():
                article_serializer.save(user=request.user)
                article_id = article_serializer.instance.id
                article = get_object_or_404(Article, id=article_id)
                bid_serializer.validated_data['article'] = article
                bid_serializer.save()
                return Response({'article': article_serializer.data, 'bid': bid_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response(article_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
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
        

class Bidding(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, article_id):
        time_zone = pytz.timezone('Asia/Seoul')
        current_time = datetime.now(time_zone)
        article = get_object_or_404(Article,id=article_id)
        bid = get_object_or_404(Bid,id=article_id)
        if bid.max_point >= int(request.data['max_point']):
            return Response({'message': "최고가보다 낮은 금액으로 입찰할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif request.user.point < int(request.data['max_point']):
            return Response({"message":"포인트가 부족합니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif bid.user == request.user:
            return Response({'message': "최고입찰자가 재입찰 할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif article.user == request.user:
            return Response({"message":"게시자는 경매에 참여할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif article.finished_at < current_time:
            return Response({"message":"이미 종료된 경매입니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:            
            serializer = BiddingSerializer(bid, data=request.data)
            if serializer.is_valid():
                if bid.user:
                    bid.user.point += bid.max_point
                    bid.user.save()
                request.user.point -= int(request.data['max_point'])
                request.user.save()
                serializer.save(user=request.user, max_point=request.data['max_point'])
                logging.warning(f"게시글 id : {article_id}  //  입찰자 id : {request.user.id}  //  입찰자 username : {request.user}  //  입찰금액 : {request.data['max_point']}")
                return Response(serializer.data)
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
