from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from rest_framework.generics import get_object_or_404
from article.models import Article, Bid
from datetime import datetime
import pytz
import logging


logging.basicConfig(filename='auction.log', level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s', encoding='utf-8')


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(close_auction, max_instances=1,
                      trigger=IntervalTrigger(seconds=10)) # 10초마다 실행
    scheduler.start()


def close_auction():
    time_zone = pytz.timezone('Asia/Seoul')
    current_time = datetime.now(time_zone)
    articles = Article.objects.all()
    close_count = 0
    close_article_list = []
    for article in articles:
        if article.finished_at < current_time:
            article.progress = False
            article.save()
            article_id = article.id
            bid_queryset = Bid.objects.filter(id=article_id)
            if bid_queryset.exists():
                bid = bid_queryset.first()
                max_bid_user = bid.max_user
                max_point = bid.max_point
                if max_bid_user is not None:
                    article.max_user = max_bid_user
                    article.max_point = max_point
                    article.save()
                    
                    article.user.point += bid.max_point
                    article.user.save()
                    
                bid.delete()
                close_count += 1
                close_article_list += [article_id]
                logging.critical(f"경매결과  //  경매 id : {article_id}  //  상품 : {article.product}  //  낙찰자 : {article.max_user}  //  낙찰금액 : {article.max_point}")
                    
    if close_count > 0:
        logging.critical(f"경매종료 집계  //  종료된 경매 수 : {close_count}  //  종료된 경매 id : {close_article_list}  //  시간 : {current_time}")