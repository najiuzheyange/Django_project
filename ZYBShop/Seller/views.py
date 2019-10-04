import random
import time
import datetime
import json
import requests

from django.shortcuts import render,HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from ZYBShop.settings import DING_URL
from Buyer.views import setPassword
from django.http import JsonResponse
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
# Create your views here.
#继续做seller视图里面的登录功能