# from apscheduler.schedulers.background import BackgroundScheduler
# from rest_framework.generics import get_object_or_404
# from rest_framework.response import Response
# from rest_framework import status, permissions
# from article.models import Article, Product, Bid
# from article.serializers import ProductUpdateSerializer
# import datetime
# import pytz


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


# scheduler = BackgroundScheduler()
# scheduler.add_job(close_auction, 'interval', seconds=30)  # 60초마다 실행
# scheduler.start()