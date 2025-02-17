from django.urls import path
import portal.features.issues.issues_views as views

urlpatterns = [
    path('all/', views.issue_list.as_view()),
    path('<uuid:issue_id>/', views.issue_detail.as_view()),
]