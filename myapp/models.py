from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUser(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    balance = models.IntegerField(default=200)


class Version(models.Model):
    version_id = models.AutoField(primary_key=True)
    is_newest = models.BooleanField(default=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    picture_id = models.ForeignKey('Picture', to_field='picture_id', on_delete=models.CASCADE)
    original_picture = models.ImageField(upload_to='static/original')
    watermark_picture = models.ImageField(upload_to='static/watermark')


class Favorite(models.Model):
    user_id = models.ForeignKey('MyUser', to_field='user_id', on_delete=models.CASCADE)
    picture_id = models.ForeignKey('Picture', to_field='picture_id', on_delete=models.CASCADE)


class PictureVersion(models.Model):
    picture_id = models.ForeignKey('Picture', to_field='picture_id', on_delete=models.CASCADE)
    version_id = models.ForeignKey('Version', to_field='version_id')


class Picture(models.Model):
    picture_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.ForeignKey('MyUser', to_field='username')
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    favorite_number = models.IntegerField()
    price = models.IntegerField()


class Download(models.Model):
    version_id = models.ForeignKey('Version', to_field='version_id')
    user_id = models.ForeignKey('MyUser', to_field='user_id')
    download_time = models.DateTimeField(auto_now_add=True)


