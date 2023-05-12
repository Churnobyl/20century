from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rest_framework.generics import get_object_or_404
from article.models import Article, Bid
from article.serializers import CloseAuctionSerializer
from datetime import datetime
import pytz


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(close_auction, max_instances=1,
                      trigger=IntervalTrigger(seconds=10)) # 10초마다 실행
    scheduler.start()


def close_auction():
    time_zone = pytz.timezone('Asia/Seoul')
    current_time = datetime.now(time_zone)
    articles = Article.objects.all()
    
    for article in articles:
        if article.finished_at < current_time:
            article.progress = False
            article.save()
            article_id = article.id
            bid_queryset = Bid.objects.filter(id=article_id)
            if bid_queryset.exists():
                bid = bid_queryset.first()
                max_bid_user = bid.user
                if max_bid_user is not None:
                    article.max_user = max_bid_user
                    article.save()
                    
                    article.user.point += bid.max_point
                    article.user.save()
                    
                    bid.delete()
                else:
                    bid.delete()
            
    print("경매종료 검사 완료")