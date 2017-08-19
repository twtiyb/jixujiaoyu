from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
import json


def index(request):
    context = {}
    context['hellow'] = 'hellow world.'
    return render(request,'polls/index.html',context)


def getQuestion(request):
    return JsonResponse('', safe=False)
