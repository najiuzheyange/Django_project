import hashlib

from Buyer.models import *
from Seller.models import *
from django.shortcuts import render,HttpResponseRedirect
from Seller.models import Login,GoodsType
from django.http import JsonResponse
from alipay import AliPay


def loginValid(fun):
    def inner(request,*args,**kwargs):
        cookie_username=request.COOKIES.get('username')
        session_username=request.session.get('username')
        if cookie_username and session_username and cookie_username==session_username:
            return fun(request,*args,**kwargs)
        return HttpResponseRedirect('/Buyer/login/')
    return inner


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



def goods_list(request,):
    """

    """
    request_type=request.GET.get('type')
    keyword=request.GET.get('keywords')
    goods_list=[]
    if request_type == 't':
        id = int(keyword)
        goods_type = GoodsType.objects.get(id=id)
        goods_list = goods_type.goods_set.order_by('-goods_pro_time')
    elif request_type == 'k':
        goods_list = Goods.objects.filter(goods_name__contains=keyword).order_by('-goods_pro_time')
    if goods_list:
        lenth = len(goods_list)/5
        if lenth != int(lenth):
            lenth += 1
        lenth = int(lenth)
        recommend = goods_list[:lenth]
    return render(request, 'buyer/goods_list.html', locals())

@loginValid
def goods_detail(request,id):
    goods=Goods.objects.get(id=int(id))
    return render(request,'buyer/detail.html',locals())

@loginValid
def user_center_info(request):
    # user_id=request.COOKIES.get("user_id")

    goods=Goods.objects.all()

    return render(request,'buyer/user_center_info.html',locals())

import time
import datetime
@loginValid
def pay_order(request):
    goods_id=request.GET.get("goods_id")
    count=request.GET.get('count')
    if goods_id and count:
        #保存订单表，但是保存总价
        order=PayOrder()
        order.order_number=str(time.time()).replace(".","")
        order.order_date=datetime.datetime.now()

        order.order_user=Login.objects.get(id=int(request.COOKIES.get("user_id")))
        order.save()
        #保存订单详情
        #查询商品信息
        goods=Goods.objects.get(id=int(goods_id))
        print(goods.goods_store)
        order_info=OrderInfo()
        order_info.order_id=order
        order_info.goods_id=int(goods_id)
        order_info.goods_picture=goods.goods_picture
        order_info.goods_name=goods.goods_name
        order_info.goods_count=int(count)
        order_info.goods_price=goods.goods_price
        order_info.goods_total_price = goods.goods_price*int(count)
        order_info.store_id = goods.goods_store
        order_info.save()
        order.order_total=order_info.goods_total_price
        order.save()
    return render(request, "buyer/pay_order.html", locals())

@loginValid
def pay_order_more(request):
    data=request.GET
    data_item = data.items()
    request_data=[]
    for key,value in data_item:
        if key.startswith("check_"):
            goods_id=key.split("_",1)[1]
            count=data.get("count_"+goods_id)
            request_data.append((int(goods_id),int(count)))
    if request_data:
        #保存订单表，但是保存总价
        order=PayOrder()
        order.order_number=str(time.time()).replace(".","")
        order.order_date=datetime.datetime.now()

        order.order_user=Login.objects.get(id=int(request.COOKIES.get("user_id")))
        order.save()
        #保存订单详情
        #查询商品信息
        order_total=0
        for goods_id,count in request_data:

            goods=Goods.objects.get(id=int(goods_id))
            order_info=OrderInfo()
            order_info.order_id=order
            order_info.goods_id=int(goods_id)
            order_info.goods_picture=goods.goods_picture
            order_info.goods_name=goods.goods_name
            order_info.goods_count=int(count)
            order_info.goods_price=goods.goods_price
            order_info.goods_total_price = goods.goods_price*int(count)
            order_info.store_id = goods.goods_store
            order_info.save()
            order_total+=order_info.goods_total_price #总价计算
        order.order_total=order_total
        order.save()
    return render(request, "buyer/pay_order.html", locals())


from ZYBShop.settings import alipay_public_key_string,alipay_private_key_string
def AlipayView(request):
    order_number=request.GET.get('order_number')
    order_total=request.GET.get("total")
    alipay = AliPay(
        appid="2016101200667732",
        app_notify_url=None,
        app_private_key_string=alipay_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no=order_number,  # 订单号
        total_amount=str(order_total),  # 支付宝金额，是字符串
        subject="食物交易",  # 支付主题
        return_url="http://127.0.0.1:8000/Buyer/pay_result/",
        notify_url="http://127.0.0.1:8000/Buyer/pay_result/"
    )  # 网页支付订单

    # 拼接收款地址 = 支付宝网关+订单返回参数
    result = "https://openapi.alipaydev.com/gateway.do?" + order_string
    return HttpResponseRedirect(result)


def pay_result(request):
    out_trade_no = request.GET.get("out_trade_no")
    if out_trade_no:
        order = PayOrder.objects.get(order_number=out_trade_no)
        order.save()
        order.orderinfo_set.all().update(order_status=1)
    return render(request, "buyer/pay_result.html", locals())

@loginValid
def cart(request):
    user_id=request.COOKIES.get("user_id")
    goods=Cart.objects.filter(cart_user=int(user_id)).order_by('-id')
    count=goods.count()
    return render(request,"buyer/cart.html",locals())


@loginValid
def add_cart(request):
    result={
        'code':200,
        'data':''
    }
    if request.method=="POST":
        id = int(request.POST.get("goods_id"))
        count = int(request.POST.get('count', 1))
        goods=Goods.objects.get(id=id)
        cart=Cart()
        cart.goods_name=goods.goods_name
        cart.goods_number=count
        cart.goods_price=goods.goods_price
        cart.goods_picture=goods.goods_picture
        cart.goods_total=goods.goods_price*count
        cart.goods_id=goods.id
        cart.cart_user=request.COOKIES.get("user_id")
        cart.save()
        result['data']='加入购物车成功'
    else:
        result['code']=500
        result['data']='请求错误，操作失败'
    return JsonResponse(result)

@loginValid
def user_center_order(request):
    user_id=request.COOKIES.get("user_id")
    user=Login.objects.get(id=int(user_id))
    order_list=user.payorder_set.order_by("-order_date")
    return render(request,'buyer/user_center_order.html',locals())
# Create your views here.
