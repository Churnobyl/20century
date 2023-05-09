from django.db import models
from user.models import User


class Article(models.Model):
    class Meta:
        db_table = ""

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
