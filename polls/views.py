from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render

# Create your views here.
from polls.models import Question
import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def getQuestion(request):
    q = Question()
    q.question_text = 'ddd'
    q.pub_date = '2017-01-22'
    q.save()

    return JsonResponse(q.json, safe=False)
