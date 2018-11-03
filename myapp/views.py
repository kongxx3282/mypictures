from django.shortcuts import render
from .models import Download, Favorite, PictureVersion, Picture, Version, MyUser

# Create your views here.
'''
def query_result(request):
    if request.method == 'POST':
        newid = []
        version = Version.objects.filter(is_newest=True)  #获取最新版本
        query_content = request.POST['content']  #获得前端内容
        query = request.POST['query'] #分类
        for v in version:
            id = v.picture_id.picture_id
            newid.append(id)
        if (query == 'all'):
            picture = Picture.objects.filter(title__icontains=query_content).filter(picture_id__in=newid)
        if (query == 'comic'):
            picture = Picture.objects.filter(title__icontains=query_content).filter(picture_id__in=newid).filter(category='comic')
        if (query == 'food'):
            picture = Picture.objects.filter(title__icontains=query_content).filter(picture_id__in=newid).filter(category='food')
        if (query == 'scenery'):
            picture = Picture.objects.filter(title__icontains=query_content).filter(picture_id__in=newid).filter(category='scenery')
        if (query == 'people'):
            picture = Picture.objects.filter(title__icontains=query_content).filter(picture_id__in=newid).filter(category='people')
        if (query == 'other'):
            picture = Picture.objects.filter(title__icontains=query_content).filter(picture_id__in=newid).filter(category='other')

        idlist = []
        for pic in picture:
            id = pic.picture_id
            idlist.append(id)
        versions = Version.objects.filter(is_newest=True).filter(picture_id__in=idlist)
        vlist = []

        for ver in versions:
            vlist.append({'pic':ver.watermark_picture,'id':ver.version_id})

        return render(request, 'query_result.html', {'vlist': vlist})
'''

def recharge(request):
    if request.method == 'POST':
        userid = request.POST['user_id']
        charge = request.POST['query']
        user = MyUser.objects.filter(username = userid)
        for u in user:
           bal = u.balance
        MyUser.objects.filter(username=userid).update(balance=bal+int(charge))

        return render(request, 'recharge.html')
    return render(request, 'recharge.html')


def home(request):
    newid = []
    alllist = []
    allversions = Version.objects.filter(is_newest=True)  # 获取最新版本
    for v in allversions:
        id = v.picture_id.picture_id
        newid.append(id)
        alllist.append({'pic': v.watermark_picture, 'id': v.version_id, 'title':v.picture_id.title})

    newversions = Version.objects.filter(is_newest=True).order_by('-upload_time')[ :10]   #按照时间降序排列取前10个
    newlist = []
    for n in newversions:
        newlist.append({'pic':n.watermark_picture,'id':n.version_id, 'title':n.picture_id.title})
    hotpicture = Picture.objects.filter(picture_id__in=newid).order_by('-favorite_number')[ :10]   #按照收藏数降序排列取前10个
    hlist = []
    for p in hotpicture:
        id = p.picture_id
        hlist.append(id)
    hotlist = []

    for h in hlist:
        for v in allversions:
            if v.picture_id.picture_id == h:
                hotlist.append({'pic': v.watermark_picture, 'id': v.version_id, 'title':v.picture_id.title})

    if request.method == 'POST':
        query_content = request.POST['content']  # 获得前端内容
        pictures = Picture.objects.filter(picture_id__in=newid).filter(title__icontains=query_content)
        list = []
        for pic in pictures:
            id = pic.picture_id
            list.append(id)
        queryversion = Version.objects.filter(is_newest=True).filter(picture_id__in=list)
        query = []
        for q in queryversion:
            query.append({'pic': q.watermark_picture, 'id': q.version_id, 'title':q.picture_id.title})
        return render(request, 'home.html', {'newlist': newlist, 'hotlist': hotlist, 'alllist': query})

    return render(request, 'home.html', {'newlist': newlist, 'hotlist': hotlist, 'alllist': alllist})

def show(request,cate):
    newid = []
    allversions = Version.objects.filter(is_newest=True)  # 获取最新版本
    for v in allversions:
        id = v.picture_id.picture_id
        newid.append(id)
    picture = Picture.objects.filter(picture_id__in=newid).filter(category=cate)
    idlist = []
    for pic in picture:
        id = pic.picture_id
        idlist.append(id)
    queryversions = Version.objects.filter(is_newest=True).filter(picture_id__in=idlist)
    querylist = []
    for q in queryversions:
        querylist.append({'pic': q.watermark_picture, 'id': q.version_id, 'title':q.picture_id.title})

    if request.method == 'POST':
        query_content = request.POST['content']  # 获得前端内容
        pictures = Picture.objects.filter(picture_id__in=newid).filter(category=cate).filter(title__icontains=query_content)
        list = []
        for pic in pictures:
            id = pic.picture_id
            list.append(id)
        queryversion = Version.objects.filter(is_newest=True).filter(picture_id__in=list)
        query = []
        for q in queryversion:
            query.append({'pic': q.watermark_picture, 'id': q.version_id, 'title':q.picture_id.title})
        return render(request, 'show.html', {'querylist': query,'cate':cate})

    return render(request, 'show.html', {'querylist': querylist,'cate':cate})


