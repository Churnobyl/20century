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
    BiddingSerializer
)
from article.serializers import BookmarkSerializer
from rest_framework.pagination import PageNumberPagination
import pytz
import datetime
from django.utils import timezone

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
    
    # 경매 끝난 거 유저가 들어오면 체크
    def check_bidding_end(self):
        check_end_article = Article.objects.filter(finished_at__lte=timezone.now()).filter(progress=1)
        check_end_article.update(progress=0)
        
    
    def get(self, request):
        self.check_bidding_end()
        articles = Article.objects.all().order_by('-created_at')
        page = self.paginate_queryset(articles)
        bids = Bid.objects.all()
        article_serializer = ArticleCreateSerializer(articles, many=True)
        bid_serializer = BidCreateSerializer(bids, many=True)
        if page is not None:
            serializer = self.get_paginated_response(self.serializer_class(page, many=True).data)
        else:
            serializer = self.serializer_class(articles, many=True)
        return Response({'article': serializer.data, 'bid': bid_serializer.data, 'article2':article_serializer.data}, status=status.HTTP_200_OK)
    
    def post(self, request):
        # 경매종료시간 finished_at의 request를 정수형으로 받고 현재시간에 더해서 저장
        request.data['finished_at'] = timezone.now() + timezone.timedelta(days=int(request.data['finished_at']))
        article_serializer = ArticleCreateSerializer(data=request.data)
        if article_serializer.is_valid():
            article_serializer.save(user=request.user)
            return Response({'article': article_serializer.data}, status=status.HTTP_200_OK)
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
        
class BiddingView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def patch(self, request, article_id):
        article = get_object_or_404(Article, id=article_id)
        if timezone.now() > article.finished_at:
            return Response({'message': "경매가 종료된 상품입니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif article.user == request.user:
            return Response({'message': "게시자는 경매에 참여할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif article.max_user == request.user:
            return Response({'message': "최고입찰자가 재입찰 할 수 없습니다."}, status=status.HTTP_400_BAD_REQUEST)
        elif article.max_point >= int(request.data['max_point']):
            return Response({'message': "최고가보다 낮습니다."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            serializer = BiddingSerializer(article, data=request.data)
            if serializer.is_valid():
                serializer.save(max_user=request.user)
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
        
        
        
# def close_auction():
#     time_zone = pytz.timezone('Asia/Seoul')
#     current_time = datetime.now(time_zone)
#     articles = Article.objects.all()
#     response_data = []
    
#     for article in articles:
#         if article.finished_at > current_time:
#             pk = article.id
#             product = get_object_or_404(Product, id=pk)
#             serializer = ProductUpdateSerializer(product)
#             if serializer.is_valid():
#                 product.progress = False
#                 serializer.save()
#                 response_data.append(serializer.data)
#             else:
#                 return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     if response_data:
#         return Response(response_data, status=status.HTTP_200_OK)
#     else:
#         return Response({"message": "종료된 경매가 없습니다."}, status=status.HTTP_200_OK)