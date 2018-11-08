from django.db import models
from django.contrib.auth.models import AbstractUser
from system.storage import ImageStorage


class MyUser(AbstractUser):
    user_id = models.AutoField(primary_key=True)
    balance = models.IntegerField(default=200)


class Version(models.Model):
    version_id = models.AutoField(primary_key=True)
    is_newest = models.BooleanField(default=True)
    upload_time = models.DateTimeField(auto_now_add=True)
    picture = models.ForeignKey('Picture', to_field='picture_id', on_delete=models.CASCADE)
    original_picture = models.ImageField(upload_to='original', storage=ImageStorage())
    watermark_picture = models.ImageField(upload_to='watermark', storage=ImageStorage())
    digital_picture = models.ImageField(upload_to='digitalmark', storage=ImageStorage())

    def __str__(self):
        return self.picture.title + str(self.version_id)


class Favorite(models.Model):
    user = models.ForeignKey('MyUser', to_field='user_id', on_delete=models.CASCADE)
    picture = models.ForeignKey('Picture', to_field='picture_id', on_delete=models.CASCADE)


class PictureVersion(models.Model):
    picture = models.ForeignKey('Picture', to_field='picture_id', on_delete=models.CASCADE)
    version = models.ForeignKey('Version', to_field='version_id')


class Picture(models.Model):
    picture_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    author = models.ForeignKey('MyUser', to_field='user_id')
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=2000)
    favorite_number = models.IntegerField(default=0)
    price = models.IntegerField()

    def __str__(self):
        return self.title


class Download(models.Model):
    version = models.ForeignKey('Version', to_field='version_id')
    user = models.ForeignKey('MyUser', to_field='user_id')
    download_time = models.DateTimeField(auto_now_add=True)


