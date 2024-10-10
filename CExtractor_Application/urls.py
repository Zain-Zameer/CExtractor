from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from CExtractor_Application import views
from django.conf.urls.static import static

urlpatterns = [
    path('',views.index,name="home"),
    path('upload/', views.upload_and_process_file, name='your_upload_view_url'),
]
