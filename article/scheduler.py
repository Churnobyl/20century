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
                      trigger=IntervalTrigger(seconds=60))
    scheduler.start()


def close_auction():
    time_zone = pytz.timezone('Asia/Seoul')
    current_time = datetime.now(time_zone)
    articles = Article.objects.all()
    for article in articles:
        if article.finished_at > current_time:
            serializer = CloseAuctionSerializer(article)
            if serializer.is_valid():
                article.progress = False
                serializer.save()
    print("실행완료")