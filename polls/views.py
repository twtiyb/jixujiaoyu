from django.core import serializers
from django.http import JsonResponse,HttpResponse
from django.shortcuts import render

# Create your views here.
from polls.models import Question
import json


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def getQuestion(request):
    questions = Question.objects.get(id=1)
    return questions.json

