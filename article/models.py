from django.db import models
from user.models import User
import os
from uuid import uuid4
from datetime import date

# 프로필 파일 이름 uuid형식으로 바꾸기
def rename_imagefile_to_uuid(instance, filename):
    now = date.today()
    upload_to = f'article/{now.year}/{now.month}/{now.day}/{instance}'
    ext = filename.split('.')[-1]
    uuid = uuid4().hex
    
    if instance:
        filename = '{}_{}.{}'.format(uuid, instance, ext)
    else:
        filename = '{}.{}'.format(uuid, ext)
    return os.path.join(upload_to, filename)

class Article(models.Model):
    class Meta:
        db_table = "article"

    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user")
    title = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField()
    category_choice = [
        (10001,'일렉츄로닉'),
        (10002,'패숑'),
        (10003,'담금주'),
        (10004,'잡화')
    ]
    category = models.IntegerField(choices=category_choice)
    product = models.CharField(max_length=100)
    progress = models.BooleanField(default=True)
    max_user = models.ForeignKey(User, null=True, default=None, on_delete=models.DO_NOTHING,related_name="max_user")
    max_point = models.IntegerField(null=True, default=None)
    
    # 아티클
    image = models.ImageField(null=True, upload_to=rename_imagefile_to_uuid, verbose_name="제품 사진")
    
    # 북마크
    bookmarked = models.ManyToManyField(User, symmetrical=False, related_name="bookmark", blank=True, verbose_name="북마크")

    def __str__(self):
        return str(self.title)
    
    
class Bid(models.Model):
    class Meta:
        db_table = "bid"
    
    article = models.ForeignKey(Article, null=True, on_delete=models.PROTECT, related_name="bid_article")
    max_user = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    max_point = models.IntegerField(default=0)
    

class Comment(models.Model):

    class Meta:
        db_table = "comment"
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
