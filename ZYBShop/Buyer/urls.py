from django.urls import path,include,re_path
from Buyer.views import *

urlpatterns = [
    path('index/', index),
    path('login/', login),
    path('register/', register),
    path('logout/', logout),
]