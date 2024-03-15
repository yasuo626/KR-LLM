
from django.conf import settings
from django.conf.urls import static
from django.template.defaulttags import url
from django.urls import path,re_path
from . import views

urlpatterns=[
    path('apiuser',views.apiuser,name='apiuser'),
    path('',views.home,name='home'),
    path('apiurl',views.wmc_apiurl,name='apiurl'),
]


