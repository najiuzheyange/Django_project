from django.shortcuts import render,HttpResponseRedirect
from Buyer.views import setPassword
from Seller.models import *



def register(request):
    error_message = ""
    if request.method =="POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email:
            user = Login.objects.filter(email=email).first()
            if not user:
                new_user = Login()
                new_user.email = email
                new_user.username = email
                new_user.password = setPassword(password)
                new_user.save()
            else:
                error_message = "邮箱已经注册，请登录"
        else:
            error_message = "邮箱不能为空"
    return render(request,"seller/register.html",locals())


def login(request):
    error_message = ''
    if request.method =='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        if email :
            user = Login.objects.filter(email=email).first()
            if user:
                db_password = user.password
                password = setPassword(password)
                if db_password ==password:
                    response = HttpResponseRedirect('/Seller/index/')
                    response.set_cookie('username',user.username)
                    response.set_cookie('user_id',user.id)
                    request.session['username'] = user.username
                    return response
                else:
                    error_message = '密码错误'
            else:
                error_message = '用户不存在'
        else:
            error_message = '邮箱不能为空'
    return render(request,'seller/login.html',locals())

def logout(request):
    response = HttpResponseRedirect("Seller/login/")
    keys = request.COOKIES.keys()
    for key in keys:
        response.delete_cookie(key)
    del request.session['username']
    return response

def index(request):
    return render(request,'seller/index.html',locals())
# Create your views here.
#继续做seller视图里面的登录功能