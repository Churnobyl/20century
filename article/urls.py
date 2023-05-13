from django.urls import path
from article import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("", views.ArticleView.as_view(), name="article_view"),
    path(
        "<int:article_id>/",
        views.ArticleDetailView.as_view(),
        name="article_detail_view",
    ),
    path("<int:article_id>/mark/",
         views.BookmarkView.as_view(), name="bookmark_view"),
    path(
        "<int:article_id>/comment/",
        views.CommentView.as_view(),
        name="comment_view",
    ),
    path(
        "<int:article_id>/comment/<int:comment_id>/",
        views.CommentDetailView.as_view(),
        name="comment_detail_view",
    ),
    path("<int:article_id>/bid/", views.Bidding.as_view(), name="bidding"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
