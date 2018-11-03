from django.shortcuts import render
from .models import Download, Favorite, PictureVersion, Picture, Version, MyUser
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse,StreamingHttpResponse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta
import json
import cv2
import pywt
import numpy

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
    condition = 0
    if request.method == 'POST':
        userid = request.POST['user_id']
        username = MyUser.objects.all()
        name = []
        for u in username:
            name.append(u.username)
        if userid not in name:
            return HttpResponse("<script >alert('用户名不存在');window.location.href='/recharge';</script>")
        charge = request.POST['query']
        user = MyUser.objects.filter(username = userid)
        for u in user:
           bal = u.balance
        MyUser.objects.filter(username=userid).update(balance=bal+int(charge))
        condition = 1

        return render(request, 'recharge.html',{"condition":json.dumps(condition)})
    return render(request, 'recharge.html', {"condition":json.dumps(condition)})


def home(request):
    user_id = request.COOKIES.get('cookie_userid')
    user_name = request.COOKIES.get('cookie_username')
    if user_name == None:
        user_name = "login"
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

    return render(request, 'home.html', {'newlist': newlist, 'hotlist': hotlist, 'alllist': alllist, 'username':user_name, 'userid':user_id})


def show(request, cate):
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

def getNewCo(img,watermark):
    a,h=pywt.dwt2(img,'Haar')
    a1,h1=pywt.dwt2(watermark,'Haar')
    n1,n2=h[0].shape
    m1,m2=h1[0].shape

<<<<<<< HEAD
    fH=numpy.zeros((n1,n2))#存放编码后的高频系数矩阵  #print(fH.shape)
    fV=numpy.zeros((n1,n2))
    fD=numpy.zeros((n1,n2))

    for i in range(n1):
        for j in range(n2):
            fH[i][j]=h[0][i][j]
            fV[i][j] = h[1][i][j]
            fD[i][j] = h[2][i][j]
    for i in range(m1):
        for j in range(m2):
            fH[i][j] = 0.1*h1[0][i][j] + fH[i][j]
            fV[i][j] = 0.1*h1[1][i][j] + fV[i][j]
            fD[i][j] = 0.1*h1[2][i][j] + fD[i][j]#以0.1的比率加上去
    F=(fH,fV,fD)
    coeffs = (a, F)
    return coeffs


def getwater(imgurl):
    img=cv2.imread(imgurl)
    watermark=cv2.imread('F:/study/DAM/watermarking/watermark.jpg')
    b,g,r=cv2.split(img)
    bw,gw,rw=cv2.split(watermark)
    coeffs_b=getNewCo(b,bw)
    coeffs_g=getNewCo(g,gw)
    coeffs_r=getNewCo(r,rw)



    imgb=pywt.idwt2(coeffs_b,'Haar')
    imgr=pywt.idwt2(coeffs_r,'Haar')
    imgg=pywt.idwt2(coeffs_g,'Haar')

    img=cv2.merge([imgb, imgg, imgr])
    cv2.imwrite(imgurl,img)


def test(request,p_id):
    username = request.COOKIES.get('cookie_username')
    if username == None:
        username = "login"
    is_download=0
    uid = request.COOKIES.get('cookie_userid')
    pic=Version.objects.filter(version_id=p_id)
    user=MyUser.objects.filter(user_id=uid)
    record=Download.objects.filter(version_id=pic,user_id=user)
    is_login=0
    if uid is not None:
        is_login=1
    if len(record)>0:
        is_download=1
    list=[]
    for i in pic:
        list.append(i)
    image_id=list[0].picture_id
    path='/'+list[0].watermark_picture.url
    image=Picture.objects.filter(picture_id=image_id.picture_id)
    image_list=[]
    for k in image:
        image_list.append(k)
    author=image_list[0].author
    description=image_list[0].description
    favourite=image_list[0].favorite_number
    price=image_list[0].price
    response=render(request,"test.html",{"p_id":json.dumps(p_id),"is_login":json.dumps(is_login),
                                         "is_download":json.dumps(is_download),"author":author,"description":description,
                                         "favourite":favourite,"price":json.dumps(price),"path":path, "username":username})
    response.set_cookie('cookie_pid',p_id)
    return response


def userlogout(request):
    response = HttpResponseRedirect('/myapp/login/')
    response.delete_cookie('cookie_userid')
    response.delete_cookie('cookie_username')
    response.delete_cookie('cookie_pid')
    logout(request)
    return response


def hide(request):
    picture_id=4
    return render(request,"hide.html",{"picture_id":picture_id})


def download_file(request):
    pid = request.COOKIES.get('cookie_pid')
    uid = request.COOKIES.get('cookie_userid')
    #if uid == None:
        #return HttpResponse("<script >alert('请先登录');window.location.href='/myapp/login';</script>")
    time = datetime.now()
    user = MyUser.objects.filter(user_id=uid)
    pic = Version.objects.filter(version_id=pid)
    record = Download.objects.filter(version_id=pic, user_id=user)
    list=[]
    for i in pic:
        temp=i.original_picture.url
        list.append(temp)
    #getwater(list[0])
    if len(record)>0:
        for i in pic:
            for j in user:
                Download.objects.create(version_id=i, user_id=j, download_time=time)
                file = open(list[0], 'rb')
                response = StreamingHttpResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment;filename="angel.png"'
                return response
    for i in user:
        for j in pic:
            if i.balance>0:
                balance=i.balance-20
                MyUser.objects.filter(user_id=i.user_id).update(balance=balance)
            else:
                return HttpResponse("<script >alert('余额不足请充值');window.location.href='/myapp/test/" + str(pid) + "';</script>")
            Download.objects.create(version_id=j, user_id=i, download_time=time)
    file = open(list[0], 'rb')
    response = StreamingHttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="angel.png"'
    return response


def collect(request):
    uid = request.COOKIES.get('cookie_userid')
    name=request.COOKIES.get('cookie_username')
    pid=request.COOKIES.get('cookie_pid')
    if uid is None:
        return HttpResponse("<script >alert('请先登录');window.location.href='/myapp/login';</script>")
    user=MyUser.objects.filter(user_id=uid)
    version=Version.objects.filter(version_id=pid)
    list=[]
    for i in version:
        pic_id=i.picture_id.picture_id
        picture=Picture.objects.filter(picture_id=pic_id)
        for j in picture:
            list.append(j)
    print(len(list))
    for i in list:
        for j in user:
            if len(Favorite.objects.filter(user_id=j,picture_id=i)) >0:

                return HttpResponse("<script >alert('已在收藏夹中');window.location.href='/myapp/test/"+str(pid)+"';</script>")
            fn=i.favorite_number+1
            Picture.objects.filter(picture_id=i.picture_id).update(favorite_number=fn)
            Favorite.objects.create(picture_id=i,user_id=j)
    return HttpResponse("<script >alert('收藏成功');window.location.href='/myapp/test/"+str(pid)+"';</script>")


def register(request):

    errors = []
    account = None
    password = None
    password2 = None
    email = None
    CompareFlag = False

    if request.method == 'POST':
        if not request.POST.get('account'):
            return HttpResponse("<script >alert('用户名不能为空');window.location.href='/myapp/register';</script>")
        else:
            account = request.POST.get('account')

        if not request.POST.get('password'):
            return HttpResponse("<script >alert('密码不能为空');window.location.href='/myapp/register';</script>")
        else:
            password = request.POST.get('password')
        if not request.POST.get('password2'):
            return HttpResponse("<script >alert('确认密码不能为空');window.location.href='/myapp/register';</script>")
        else:
            password2 = request.POST.get('password2')

        if password is not None:
            if password == password2:
                CompareFlag = True
            else:
                return HttpResponse("<script >alert('两次输入密码不一致');window.location.href='/myapp/register';</script>")

        if account is not None and password is not None and password2 is not None  and CompareFlag :
            user_check = MyUser.objects.filter(username=account)
            if (len(user_check)) > 0:
                return HttpResponse("<script >alert('用户名已存在');window.location.href='/myapp/register';</script>")
            else:
                user = MyUser.objects.create_user(username=account,email=None,password=password)

                user.balance=200
                user.save()
                id=user.user_id
                response = HttpResponseRedirect('/home/')
                response.set_cookie('cookie_username', account)
                response.set_cookie('cookie_userid', id)
                return response

    return render(request,'register.html', {'errors': errors})


def my_login(request):
    errors =[]
    account = None
    password = None
    p_id=request.COOKIES.get('cookie_pid')
    if request.method == "POST":
        if not request.POST.get('account'):
            return HttpResponse("<script >alert('请填写用户名');window.location.href='/myapp/login';</script>")
        else:
            account = request.POST.get('account')

        if not request.POST.get('password'):
            return HttpResponse("<script >alert('请填写密码');window.location.href='/myapp/login';</script>")
        else:
            password = request.POST.get('password')
        if account is not None and password is not None:
            user = authenticate(username=account,password=password)


            if user is not None:
                if user.is_active:
                    if p_id is not None:
                        id = user.user_id
                        name=user.username

                        response = HttpResponseRedirect('/myapp/test/'+str(p_id))
                        response.set_cookie('cookie_username', name)
                        response.set_cookie('cookie_userid', id)
                        return response
                    else:
                        id = user.user_id
                        name = user.username
                        response = HttpResponseRedirect('/home/')
                        response.set_cookie('cookie_username', name)
                        response.set_cookie('cookie_userid', id)
                        return response


            else:
                return HttpResponse("<script >alert('用户名密码错误');window.location.href='/myapp/login';</script>")

    return render(request,'login.html', {'errors': errors})
=======
def usercenter_index(request):
    return render(request, 'usercenter/usercenter.html')


def upload(request):
    return render(request, 'usercenter/upload.html')


def edit(request):
    return render(request, 'usercenter/edit.html')


def myfavorite(request):
    return render(request, 'usercenter/myfavorite.html')
>>>>>>> 900fbb686fd212cdcf7c2b98a9f2fc4270b024da
