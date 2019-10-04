from django.urls import path,include,re_path
from Buyer.views import *

urlpatterns = [
    path('index/', index),
    path('login/', login),
    path('register/', register),
    path('logout/', logout),
    path('goods_list/',goods_list),
    path('logout/',logout),
    path('user_center/',user_center_info),
    re_path('goods_detail/(?P<id>\d+)/',goods_detail),
    path('pay_order/',pay_order),
    path('alipay/',AlipayView),
    path('pay_result/',pay_result),
    path('add_cart/',add_cart),
    path('cart/',cart),
    path('pay_order_more/',pay_order_more),
    path('uco/',user_center_order),
]