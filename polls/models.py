# Create your models here.
from django.db import models
from jsonfield import JSONField



class Exam(models.Model):
    id = models.CharField(primary_key=True,max_length=30)
    name = models.CharField(max_length=50)
    testFinish = models.BooleanField(default=False)

class Question(models.Model):
    question = models.ForeignKey(Exam, on_delete=models.CASCADE)
    id = models.CharField(primary_key=True,max_length=30)
    question_text = models.CharField(max_length=200)

class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
