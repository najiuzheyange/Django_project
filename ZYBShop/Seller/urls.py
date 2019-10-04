
from django.urls import path,re_path

from Seller.views import *


urlpatterns = [
    path('register/',register),
    path('login/', login),
    path('index/', index),
    path('logout/', logout),
    path('slc/', send_login_code),
    path('goods_add/',goods_add),
    path("personal_info/", personal_info),
    re_path('gl/(?P<page>\d+)/(?P<status>[01])/', goods_list),
]