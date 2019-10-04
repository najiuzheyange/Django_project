import hashlib


from django.shortcuts import render,HttpResponseRedirect
from Seller.models import Login,GoodsType


def setPassword(password):
    m=hashlib.md5()
    m.update(password.encode())
    result = m.hexdigest()
    return result

def logout(request):
    url=request.META.get("HTTP_REFERER",'/Buyer/index/')
    response = HttpResponseRedirect(url)
    for k in request.COOKIES :
        response.delete_cookie(k)
    del request.session["username"]
    return response


def login(request):
    if request.method =="POST":
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        if email :
            user = Login.objects.filter(email=email).first()
            if user:
                db_password = user.password
                password = setPassword(password)
                if db_password == password :
                    response=HttpResponseRedirect('/Buyer/index/')
                    response.set_cookie("username",user.username)
                    response.set_cookie("user_id",user.id)
                    request.session["username"] = user.username
                    return response
    return render(request,'buyer/login.html',locals())


def register(request):
    if request.method =="POST":
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        if email :
            user = Login.objects.filter(email=email).first()
            if not user:
                user = Login()
                user.username = username
                user,password = setPassword(password)
                user.email = email
                user.seve()
    return render(request,'buyer/register.html',locals())

def index(request):
    goods_type=GoodsType.objects.all()
    result=[]
    for ty in goods_type:
        goods = ty.goods_set.order_by("-goods_pro_time")
        if len(goods)>=4:
            goods=goods[:4]
            result.append({"type":ty,"goods_list":goods})
    return render(request,'buyer/index.html',locals())

# Create your views here.
