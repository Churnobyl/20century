from django.db import models
from user.models import User


class Article(models.Model):
    class Meta:
        db_table = "article"

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    finished_at = models.DateTimeField()
    
    # 북마크
    bookmarked = models.ManyToManyField(User, symmetrical=False, related_name="bookmark", blank=True, verbose_name="북마크")

    def __str__(self):
        return str(self.title)
    

class Product(models.Model):
    class Meta:
        db_table = "product"
        
    name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    progress = models.BooleanField(default=True)

    def __str__(self):
        return str(self.name)
    

class Comment(models.Model):
    
    class Meta:
        db_table = "comment"
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
