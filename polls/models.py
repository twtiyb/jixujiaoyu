# Create your models here.
from django.db import models


class User(models.Model):
    """
    网站用户
    """
    name = models.CharField(primary_key=True, max_length=30)
    password = models.CharField(max_length=30)

    invent_code = models.CharField(max_length=30)


class Account(models.Model):
    """
    专业技能培训帐户密码
    """
    pass_id = models.CharField(primary_key=True, max_length=30)
    password = models.CharField( max_length=30)


class Pay(models.Model):
    """
    支付记录
    """
    total_fee = models.FloatField()
    # 0 未支付  10已支付
    status = models.IntegerField()

    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Invent(models.Model):
    """
    邀请记录
    """
    invitee = models.ForeignKey(User, related_name='invitee', on_delete=models.CASCADE)
    inventor = models.ForeignKey(User, related_name='inventor', on_delete=models.CASCADE)
