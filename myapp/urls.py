from django.contrib import admin
from django.conf.urls import include, url
from myapp import  views
urlpatterns = [
url(r'^test/(\w+)',views.test),
    url(r'^login/',views.my_login),
    url(r'^hide/',views.hide),
    url(r'^register/',views.register),

    url(r'^download', views.download_file,name="download"),
    url(r'^collect',views.collect,name='collect'),
    url(r'^logout/$',views.userlogout, name = 'logout'),

]
