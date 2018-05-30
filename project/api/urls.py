from django.urls import path
from django.http import JsonResponse
from . import views
from django.conf.urls import url

urlpatterns = [
    path('v1/tasks/', views.tasks, name='tasks'),
    url(r'^search_queue/$', views.SearchQueue.as_view())
]

# https://docs.djangoproject.com/en/2.0/releases/2.0/#simplified-url-routing-syntax
