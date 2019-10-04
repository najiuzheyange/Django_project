
from django.urls import path

from Seller.views import *


urlpatterns = [
    path('register/',register),
    path('login/', login),
    path('index/', index),
    path('logout/', logout),
]