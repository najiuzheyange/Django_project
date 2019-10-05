import random
import time
import datetime
import json
import requests

from django.shortcuts import render,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from ZYBShop.settings import DING_URL
from Buyer.views import setPassword
from django.http import JsonResponse
from Seller.models import *

def loginValid(func):
    def inner(request,*args,**kwargs):
        cookie_username = request.COOKIES.get('username')
        session_username = request.session.get('username')
        if session_username and cookie_username and session_username==cookie_username:
            return func(request, *args,**kwargs)
        else:
            return HttpResponseRedirect("/Seller/login/")
    return inner

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
        code = request.POST.get("valid_code")
        if email :
            user = Login.objects.filter(email=email).first()
            if user:
                db_password = user.password
                password = setPassword(password)
                if db_password ==password:
                    #检测验证码和获取验证码
                    codes = ValidCode.objects.filter(code_user=email).order_by("-code_time").first()
                    #校验验证码是否存在，是否过期，是否被使用
                    now = time.mktime(datetime.datetime.now().timetuple())
                    db_time = time.mktime(codes.code_time.timetuple())
                    t = (now-db_time)/60
                    if codes and codes.code_state ==0 and t<=5 and codes.code_content.upper()==code.upper():
                        response = HttpResponseRedirect('/Seller/index/')
                        response.set_cookie('username',user.username)
                        response.set_cookie('user_id',user.id)
                        request.session['username'] = user.username
                        return response
                    else:
                        error_message="验证码错误"
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

#校验功能开始
#生成随机数验证码,通常默认为六位数
def random_code(len=6):
    string="1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    valid_code = "".join([random.choice(string) for i in range(len)])
    return valid_code

#通过钉钉发送验证码
def sendDing(content,to=None):
    headers = {
        "Content-Type":"application/json",
        "Charset":"utf-8"
    }
    requests_data = {
        "msgtype":"text",
        "text":{
            "content":content
        },
        "at":{
            "atMobiles":[],
            "isAtAll":True
        }
    }
    if to :
        requests_data["at"]["atMobiles"].append(to)
        requests_data["at"]["isAtAll"]=False
    else:
        requests_data["at"]["atMobiles"].clear()
        requests_data["at"]["isAtAll"] = True
    sendData = json.dumps(requests_data)
    response = requests.post(url=DING_URL,headers=headers,data=sendData)
    content = response.json()
    return content

#保存验证码
@csrf_exempt
def send_login_code(request):
    result={
        "code":200,
        "data":""
    }
    if request.method =="POST":
        email = request.POST.get("email")
        code = random_code()
        c = ValidCode()
        c.code_user = email
        c.code_content = code
        c.save()
        send_data="%s的验证码是%s,打死也不要告诉别人"%(email,code)
        sendDing(send_data)
        result["data"]="发送成功"
    else:
        result["code"]=400
        result["data"]="请求错误"
    return JsonResponse(result)

#商品操作
@loginValid
def goods_list(request, status, page=1):
    user_id=request.COOKIES.get('user_id')
    user=Login.objects.get(id=int(user_id))
    page = int(page)
    if status == "1":
        goodses = Goods.objects.filter(goods_store=user, goods_status=1)
        goods_types="在售商品"
    elif status == '0':
        goodses=Goods.objects.filter(goods_store=user, goods_status=0)
        goods_types="下架商品"
    else:
        goodses = Goods.objects.all()  #获取所有的信息
    all_goods = Paginator(goodses, 10)    #分页
    goods_list = all_goods.page(page)     #生成所对应页码的所有信息
    return render(request, 'seller/good_list.html', locals())

@loginValid
def personal_info(request):
    user_id = request.COOKIES.get("user_id")
    user = Login.objects.get(id=int(user_id))
    if request.method == "POST":
        user.username = request.POST.get("username")
        user.gender = request.POST.get("gender")
        user.age = request.POST.get("age")
        user.phone_number = request.POST.get("phone_number")
        user.address = request.POST.get("address")
        user.photo = request.FILES.get("photo")
        user.save()
    return render(request, "seller/personal_info.html", locals())

@loginValid
def goods_add(request):
    goods_type_list=GoodsType.objects.all()
    if request.method == "POST":
        data=request.POST
        files=request.FILES

        goods=Goods()
        goods.goods_number=data.get('goods_number')
        goods.goods_name=data.get('goods_name')
        goods.goods_price=data.get('goods_price')
        goods.goods_count=data.get('goods_count')
        goods.goods_location=data.get('goods_location')
        goods.goods_safe_date=data.get('goods_safe_date')
        goods.goods_pro_time=data.get('goods_pro_time')
        goods.goods_status=1

        goods_type_id =int(data.get("goods_type"))
        goods.goods_type=GoodsType.objects.get(id=goods_type_id)

        goods.goods_picture=files.get('picture')

        user_id=request.COOKIES.get('user_id')
        goods.goods_store=Login.objects.get(id=int(user_id))
        goods.save()
    return render(request,"seller/goods_add.html",locals())

@loginValid
def goods_status(request, state, id):
    id = int(id)
    goods=Goods.objects.get(id=id)
    if state == "up":
        goods.goods_status = 1
    elif state == 'down':
        goods.goods_status = 0
    goods.save()
    url=request.META.get("HTTP_REFERER", '/Seller/gl/1/1')
    return HttpResponseRedirect(url)

def order_list(request,status):
    """
    status订单的状态
    0未支付
    1已支付
    2待收货
    3/4 完成/拒收
    :param request:
    :param status:
    :return:
    """
    status=int(status)

    user_id=request.COOKIES.get("user_id")  #获取店铺id
    store=Login.objects.get(id=user_id)     #获取店铺信息
    store_order=store.orderinfo_set.filter(order_status=status).order_by("-id")    #获取该店铺的所有订单信息
    # order_list=Login.objects.get(id=int(user_id)).orderinfo_set.all()
    return render(request,"seller/order_list.html",locals())

from Buyer.models import OrderInfo
def change_order(request):
    #通过订单详情id来锁定订单详情
    order_id=request.GET.get("order_id")
    #获取要修改的状态
    order_status=request.GET.get("order_status")
    order=OrderInfo.objects.get(id=order_id)
    order.order_status = int(order_status)
    order.save()
    return JsonResponse({'data':"修改成功"})
# Create your views here.
#继续做seller视图里面的登录功能