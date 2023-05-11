from django.apps import AppConfig
from centurymuseum import settings


class ArticleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'article'

    # def ready(self):
    #     if settings.SCHEDULER_DEFAULT:
    #         from . import scheduler
    #         scheduler.start()
