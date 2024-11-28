from django.urls import path
from .views import DiscussionListView, DiscussionCreateView, DiscussionDetailView, CommentCreateView, CommentListView, \
    DiscussionUpdateStatusView, DiscussionMarkCommentView

urlpatterns = [
    path('list/', DiscussionListView.as_view(), name='discussion-list'),
    path('create/', DiscussionCreateView.as_view(), name='discussion-create'),
    path('<int:pk>/update-status/', DiscussionUpdateStatusView.as_view(), name='discussion-update-status'),
    path('<int:pk>/mark-comment/', DiscussionMarkCommentView.as_view(), name='discussion-mark-comment'),
    path('<int:pk>/', DiscussionDetailView.as_view(), name='discussion-detail'),
    path('<int:discussion_id>/comments/', CommentListView.as_view(), name='comment-list'),
    path('<int:discussion_id>/comments/create/', CommentCreateView.as_view(), name='comment-create'),
]
