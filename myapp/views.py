from django.shortcuts import render
from .models import Download, Favorite, PictureVersion, Picture, Version, MyUser
from django.http import HttpRequest, HttpResponseRedirect, HttpResponse,StreamingHttpResponse
from django.contrib.auth import authenticate, login, logout
from datetime import datetime, timedelta
import json
#import cv2
#import pywt
import numpy
from django.conf.urls.static import static
from PIL import Image, ImageDraw, ImageFont
from django.core.files.base import ContentFile
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# Create your views here.
def recharge(request):
    user_name = request.COOKIES.get('cookie_username')
    useri = MyUser.objects.filter(username=user_name)
    for u in useri:
        bala = u.balance
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
        for u in useri:
            bala = u.balance

            return HttpResponse("<script >alert('充值成功！');window.location.href='/recharge';</script>")
    return render(request, 'recharge.html', {"balance":bala, 'username':user_name})


def home(request):
    user_id = request.COOKIES.get('cookie_userid')
    user_name = request.COOKIES.get('cookie_username')
    if user_name == None:
        user_name = "login"
    newid = []
    alllist = []
    allversions = Version.objects.filter(is_newest=True)  # 获取最新版本
    for v in allversions:
        id = v.picture.picture_id
        newid.append(id)
        alllist.append({'pic': v.watermark_picture.url, 'id': v.version_id, 'title':v.picture.title})

    newversions = Version.objects.filter(is_newest=True).order_by('-upload_time')[ :12]   #按照时间降序排列取前10个
    newlist = []
    for n in newversions:
        newlist.append({'pic':n.watermark_picture.url,'id':n.version_id, 'title':n.picture.title})

    hotpicture = Picture.objects.filter(picture_id__in=newid).order_by('-favorite_number')[ :11]   #按照收藏数降序排列取前10个
    hlist = []
    for p in hotpicture:
        id = p.picture_id
        hlist.append(id)
    hotlist = []

    for h in hlist:
        for v in allversions:
            if v.picture.picture_id == h:
                hotlist.append({'pic': v.watermark_picture.url, 'id': v.version_id, 'title':v.picture.title})

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
            query.append({'pic': q.watermark_picture.url, 'id': q.version_id, 'title':q.picture.title})
        return render(request, 'home.html', {'newlist': newlist, 'hotlist': hotlist, 'alllist': query, 'username':user_name})

    return render(request, 'home.html', {'newlist': newlist, 'hotlist': hotlist, 'alllist': alllist, 'username':user_name, 'userid':user_id})


def show(request, cate):
    user_name = request.COOKIES.get('cookie_username')
    if user_name == None:
        user_name = "login"
    newid = []
    allversions = Version.objects.filter(is_newest=True)  # 获取最新版本
    for v in allversions:
        id = v.picture.picture_id
        newid.append(id)
    picture = Picture.objects.filter(picture_id__in=newid).filter(category=cate)
    idlist = []
    for pic in picture:
        id = pic.picture_id
        idlist.append(id)
    queryversions = Version.objects.filter(is_newest=True).filter(picture_id__in=idlist)
    querylist = []
    for q in queryversions:
        querylist.append({'pic': q.watermark_picture.url, 'id': q.version_id, 'title':q.picture.title})

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
            query.append({'pic': q.watermark_picture.url, 'id': q.version_id, 'title':q.picture.title})
        return render(request, 'show.html', {'querylist': query,'cate':cate, 'username':user_name})

    return render(request, 'show.html', {'querylist': querylist,'cate':cate, 'username':user_name})


def getNewCo(img,watermark):
    a,h=pywt.dwt2(img,'Haar')
    a1,h1=pywt.dwt2(watermark,'Haar')
    n1,n2=h[0].shape
    m1,m2=h1[0].shape

    fH=numpy.zeros((n1,n2))
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
    img=cv2.imread('media/'+imgurl)
    watermark=cv2.imread('static/markers/marker.png')
    version=Version.objects.filter(original_picture=imgurl)
    list=[]
    for i in version:
        list.append(i.version_id)
    print(len(list))
    saveurl='media/digitalmark/encode'+str(list[0])+'.png'
    b,g,r=cv2.split(img)
    bw,gw,rw=cv2.split(watermark)
    coeffs_b=getNewCo(b,bw)
    coeffs_g=getNewCo(g,gw)
    coeffs_r=getNewCo(r,rw)

    imgb=pywt.idwt2(coeffs_b,'Haar')
    imgr=pywt.idwt2(coeffs_r,'Haar')
    imgg=pywt.idwt2(coeffs_g,'Haar')

    img=cv2.merge([imgb, imgg, imgr])
    cv2.imwrite(saveurl,img)
    Version.objects.filter(original_picture=imgurl).update(digital_picture=saveurl)
    return saveurl

def test(request,p_id):
    username = request.COOKIES.get('cookie_username')
    if username == None:
        username = "login"
    is_download=0
    uid = request.COOKIES.get('cookie_userid')
    pic=Version.objects.filter(version_id=p_id)
    user=MyUser.objects.filter(user_id=uid)
    record=Download.objects.filter(version=pic, user=user)
    is_login=0
    if uid is not None:
        is_login=1
    if len(record)>0:
        is_download=1
    list=[]
    for i in pic:
        list.append(i)
    image_id=list[0].picture
    path=list[0].watermark_picture.url
    image=Picture.objects.filter(picture_id=image_id.picture_id)
    image_list=[]
    for k in image:
        image_list.append(k)
    is_myself=0
    if uid is not None:

        if image_list[0].author.user_id==int(uid):
            is_myself=1

    author=image_list[0].author
    description=image_list[0].description
    favourite=image_list[0].favorite_number
    price=image_list[0].price
    title=image_list[0].title
    category=image_list[0].category
    response=render(request,"test.html",{"p_id":json.dumps(p_id),"title":title,"category":category,"is_login":json.dumps(is_login),
                                         "is_download":json.dumps(is_download),"author":author,"description":description,
                                         "favourite":favourite,"price":json.dumps(price),"path":path, "username":username,'is_myself':json.dumps(is_myself)})
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
    list_p=[]
    for k in pic:
        picture=Picture.objects.filter(picture_id=k.picture.picture_id)
        list_p.append(picture)
    author_list=[]
    for o in list_p[0]:
        author=MyUser.objects.filter(user_id=o.author.user_id)
        author_list.append(author)

    list_price=[]
    list_name=[]
    for i in list_p[0]:
        list_price.append(i.price)
        list_name.append(i.title)
    record = Download.objects.filter(version=pic, user=user)
    list=[]
    for i in pic:
        temp=i.digital_picture.url
        list.append(temp)
    print(list[0])

    #digital=getwater(list[0][7:])
    #print(digital)
    if len(record)>0:
        for i in pic:
            for j in user:
                Download.objects.create(version=i, user=j, download_time=time)
                file = open(list[0][1:], 'rb')
                response = StreamingHttpResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                strg='attachment;filename="download.png"'
                response['Content-Disposition'] = strg
                return response
    for i in author_list[0]:
        for j in user:
            print(i.user_id)
            print(j.user_id)
            if i.user_id==j.user_id:
                file = open(list[0][1:], 'rb')
                response = StreamingHttpResponse(file)
                response['Content-Type'] = 'application/octet-stream'
                strg = 'attachment;filename="download.png"'
                response['Content-Disposition'] = strg
                return response


    for i in user:
        for j in pic:
            for k in author_list[0]:
                if i.balance>0 :
                    balance=i.balance-list_price[0]
                    balance2=k.balance+list_price[0]
                    MyUser.objects.filter(user_id=i.user_id).update(balance=balance)
                    MyUser.objects.filter(user_id=k.user_id).update(balance=balance2)

                else:
                    return HttpResponse("<script >alert('余额不足请充值');window.location.href='/myapp/test/" + str(pid) + "';</script>")

                Download.objects.create(version=j, user=i, download_time=time)

    file = open(list[0][1:], 'rb')
    response = StreamingHttpResponse(file)
    response['Content-Type'] = 'application/octet-stream'
    strg = 'attachment;filename="download.png"'
    response['Content-Disposition'] = strg
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
        pic_id=i.picture.picture_id
        picture=Picture.objects.filter(picture_id=pic_id)
        for j in picture:
            list.append(j)
    print(len(list))
    for i in list:
        for j in user:
            if len(Favorite.objects.filter(user=j,picture=i)) >0:

                return HttpResponse("<script >alert('已在收藏夹中');window.location.href='/myapp/test/"+str(pid)+"';</script>")
            fn=i.favorite_number+1
            Picture.objects.filter(picture_id=i.picture_id).update(favorite_number=fn)
            Favorite.objects.create(picture=i,user=j)
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



def usercenter_index(request):
    user_id = request.COOKIES.get('cookie_userid')
    user_name = request.COOKIES.get('cookie_username')
    user = MyUser.objects.get(user_id=user_id)
    pictures = user.picture_set.all()
    ver_list = []
    for pic in pictures:
        versions = pic.version_set.all()
        for ver in versions:
            if ver.is_newest:
                ver_list.append(ver)
                break
    return render(request, 'usercenter/usercenter.html', {'user_id': user_id, 'username': user_name, 'ver_list': ver_list})


def upload(request):
    user_name = request.COOKIES.get('cookie_username')
    return render(request, 'usercenter/upload.html',{'username':user_name})


def handle_upload(request):
    if request.method == "POST":
        new_picture = Picture()
        user_id = request.COOKIES.get('cookie_userid')
        new_picture.author = MyUser.objects.get(user_id=user_id)
        new_picture.title = request.POST.get('title')
        new_picture.category = request.POST.get('category')
        new_picture.description = request.POST.get('description')
        new_picture.favorite_number = 0
        new_picture.price = request.POST.get('price')
        new_picture.save()

        new_version = Version()
        original_picture = request.FILES['original']

        new_version.original_picture = original_picture
        new_version.picture = new_picture
        new_version.watermark_picture = addmarker(original_picture)
        new_version.digital_picture = addwatermarker(original_picture)
        new_version.save()

        response = HttpResponse("<script>alert('上传成功');window.location.href='/usercenter/upload/';</script>")
        return response
    else:
        response = HttpResponse("<script>alert('上传失败');window.location.href='/usercenter/upload/';</script>")
        return response


def edit(request, picture_id):
    user_name = request.COOKIES.get('cookie_username')


    if request.method == "POST":
        edit_pic = Picture.objects.get(pk=picture_id)
        edit_pic.title = request.POST.get('title')
        edit_pic.category = request.POST.get('category')
        edit_pic.description = request.POST.get('description')
        edit_pic.price = request.POST.get('price')
        edit_pic.save()

        if request.FILES.get('new_version') is not None:
            pic = Picture.objects.get(pk=picture_id)
            versions = pic.version_set.all()
            for ver in versions:
                if ver.is_newest:
                    ver.is_newest = False
                    ver.save()
            new_version = Version()
            original_picture = request.FILES['new_version']
            new_version.original_picture = original_picture
            new_version.picture = pic
            new_version.watermark_picture = addmarker(original_picture)
            new_version.digital_picture = addwatermarker(original_picture)
            new_version.save()

    picture = Picture.objects.get(pk=picture_id)
    versions = picture.version_set.all()
    for ver in versions:
        if ver.is_newest:
            newest_ver = ver
    return render(request, 'usercenter/edit.html', {'picture': picture, 'newest_ver': newest_ver, 'versions': versions,'username':user_name})


def set_ver_version(request, version_id):
    pic = Version.objects.get(pk=version_id).picture
    old_ver = pic.version_set.get(is_newest=True)
    old_ver.is_newest = False
    old_ver.save()
    new_ver = pic.version_set.get(version_id=version_id)
    new_ver.is_newest = True
    new_ver.save()
    return HttpResponse("<script >alert('设置成功');window.location.href='/usercenter/edit/" + str(pic.picture_id) + "';</script>")


def delete_picture(request, picture_id):
    pic = Picture.objects.get(pk=picture_id)
    pic.delete()
    response = HttpResponse("<script>window.location.href='/usercenter/';</script>")
    return response


def cancel_favorite(request, picture_id):
    user_id = request.COOKIES.get('cookie_userid')
    user = MyUser.objects.get(user_id=user_id)
    favo = Favorite.objects.filter(user=user).filter(picture_id=picture_id)
    favo.delete()

    response = HttpResponse("<script>window.location.href='/usercenter/myfavorite/';</script>")
    return response


def myfavorite(request):
    user_name = request.COOKIES.get('cookie_username')
    user_id = request.COOKIES.get('cookie_userid')
    user = MyUser.objects.get(user_id=user_id)
    favorites = Favorite.objects.filter(user=user)
    pictures = []
    for favo in favorites:
        pictures.append(favo.picture)
    ver_list = []
    for pic in pictures:
        versions = pic.version_set.all()
        for ver in versions:
            if ver.is_newest:
                ver_list.append(ver)
                break
    return render(request, 'usercenter/myfavorite.html', {'ver_list': ver_list, 'username': user_name})


def addmarker(original_picture):
    base_image = Image.open(original_picture)
    watermark = Image.open('static/markers/marker.png')
    longer_edge = 0 if base_image.size[0] > base_image.size[1] else 1

    if longer_edge == 1:
        new_width = watermark.size[0]
        new_length = int(watermark.size[0] * base_image.size[1] / base_image.size[0])
        base_image = base_image.resize((new_width, new_length))
        transparent = Image.new('RGBA', (new_width, new_length), (0, 0, 0, 0))
        transparent.paste(base_image, (0, 0))
        transparent.paste(watermark, (0, int((new_length - watermark.size[1]) / 2)), mask=watermark)
    else:
        new_width = int(watermark.size[1] * base_image.size[0] / base_image.size[1])
        new_length = watermark.size[1]
        base_image = base_image.resize((new_width, new_length))
        transparent = Image.new('RGBA', (new_width, new_length), (0, 0, 0, 0))
        transparent.paste(base_image, (0, 0))
        transparent.paste(watermark, (int((new_width - watermark.size[0]) / 2), 0), mask=watermark)

    pic_io = BytesIO()
    transparent.convert('RGB').save(pic_io, 'png')

    pic_file = InMemoryUploadedFile(
        file=pic_io,
        field_name=None,
        name=original_picture.name,
        content_type=original_picture.content_type,
        size=original_picture.size,
        charset=None
    )
    return pic_file


def addwatermarker(original_picture):
    hide = Image.open(original_picture)
    img = Image.open("static/markers/copyright.png")
    img = img.resize(hide.size)
    original = img.convert("P")

    height1 = hide.size[0]
    width1 = hide.size[1]
    height2 = original.size[0]
    width2 = original.size[1]

    # 新建图片
    result = Image.new("RGB", (height1, width1))

    # 图片隐写
    for i in range(0, height2):
        for j in range(0, width2):
            pix = original.getpixel((i, j))
            # 提取像素的第7、8位
            tmp1 = pix >> 6
            tmp1 = tmp1 & 3
            # 将提取后的值写入隐藏图片同位置像素R通道的最后两位
            bit1_hide = hide.getpixel((i, j))[0]
            bit1_hide = ((bit1_hide >> 2) << 2) + tmp1
            # 提取像素的第4、5、6位
            tmp2 = pix >> 3
            tmp2 = tmp2 & 7
            # 将提取后的值写入隐藏图片同位置像素G通道的最后三位
            bit2_hide = hide.getpixel((i, j))[1]
            bit2_hide = ((bit2_hide >> 3) << 3) + tmp2
            # 提取像素的第1、2、3位
            tmp3 = pix & 7
            # 将提取后的值写入隐藏图片同位置像素B通道的最后三位
            bit3_hide = hide.getpixel((i, j))[2]
            bit3_hide = ((bit3_hide >> 3) << 3) + tmp3
            # 将修改后的RGB值写入新建图片同位置像素中
            result.putpixel([i, j], (bit1_hide, bit2_hide, bit3_hide))

    pic_io = BytesIO()
    result.convert('RGB').save(pic_io, 'png')

    pic_file = InMemoryUploadedFile(
        file=pic_io,
        field_name=None,
        name=original_picture.name,
        content_type=original_picture.content_type,
        size=original_picture.size,
        charset=None
    )

    return pic_file
