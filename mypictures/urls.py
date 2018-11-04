"""mypictures URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from myapp import views
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^recharge/', views.recharge, name='recharge'),
    url(r'^home/', views.home, name="home"),
    url(r'^show/(\w+)', views.show),

    url(r'^myapp/', include('myapp.urls', namespace='myapp')),



    # /usercenter/
    url(r'usercenter/$', views.usercenter_index, name='index'),
    # /usercenter/upload
    url(r'usercenter/upload/$', views.upload, name='upload'),
    # /usercenter/edit
    url(r'usercenter/edit/$', views.edit, name='edit'),
    # usercenter/myfavorite
    url(r'usercenter/myfavorite/$', views.myfavorite, name='myfavorite'),
    # usercenter/recharge
    # url(r'recharge/$', views.recharge, name='recharge'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
