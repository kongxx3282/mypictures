from django.contrib import admin
from .models import MyUser, Version, Favorite, PictureVersion, Picture, Download
# Register your models here.

admin.site.register(MyUser)
admin.site.register(Version)
admin.site.register(Favorite)
admin.site.register(PictureVersion)
admin.site.register(Picture)
admin.site.register(Download)