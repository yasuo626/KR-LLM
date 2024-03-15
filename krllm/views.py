import os
import pathlib

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.http import JsonResponse
from django.shortcuts import redirect

from wmc.models import User
from wmc.views import get_apiurl
import requests, json
import datetime
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.http import JsonResponse

def krllm_home(request):

    content={}
    content['require_login']="1"
    if request.user.is_authenticated:
        content['is_login']=1
        content['username']=request.user.username
    else:
        content['is_login']="0"
        content['username']="unlogin"
    content['apiurl'] = get_apiurl()
    template=loader.get_template('krllm/home.html')
    return HttpResponse(template.render(content,request))

def krllm_kb(request):
    content={}
    content['require_login']="1"
    if not request.user.is_authenticated:
        return redirect('../krllm/')
    template=loader.get_template('krllm/kb.html')
    content['username'] = request.user.username
    content['apiurl'] = get_apiurl()
    return HttpResponse(template.render(content,request))

def krllm_file(request):
    content={}
    content['require_login']="1"
    if not request.user.is_authenticated:
        return redirect('../krllm/')
    template=loader.get_template('krllm/file.html')
    content['username'] = request.user.username
    content['apiurl'] = get_apiurl()
    return HttpResponse(template.render(content,request))
def krllm_chat(request):
    content={}
    if not request.user.is_authenticated:
        return redirect('../krllm/')
    template=loader.get_template('krllm/chat.html')
    content['username'] = request.user.username
    content['apiurl'] = get_apiurl()
    return HttpResponse(template.render(content,request))

