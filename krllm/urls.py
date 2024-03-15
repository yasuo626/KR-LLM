
from django.conf import settings
from django.conf.urls import static
from django.template.defaulttags import url
from django.urls import path,re_path
from . import views

urlpatterns=[
    path('',views.krllm_home,name='main'),
    path('kb',views.krllm_kb,name='kb'),
    path('file',views.krllm_file,name='file'),
    path('chat',views.krllm_chat,name='chat'),
]


