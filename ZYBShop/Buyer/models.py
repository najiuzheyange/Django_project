from django.db import models
from Seller.models import Login

class PayOrder(models.Model):
    """
    订单表
    订单状态:
        0未支付
        1已支付
        2待发货
        3待收货
        4/5完成/拒收
    """
    order_number=models.CharField(max_length=32)
    order_date=models.DateTimeField(auto_now=True)
    # order_status=models.IntegerField()
    order_total=models.FloatField(blank=True,null=True)
    order_user=models.ForeignKey(to=Login,on_delete=models.CASCADE)

class OrderInfo(models.Model):
    """
    订单详情表
    """
    order_id=models.ForeignKey(to=PayOrder,on_delete=models.CASCADE)
    goods_id=models.IntegerField()
    goods_picture=models.CharField(max_length=32)
    goods_name=models.CharField(max_length=32)
    goods_count=models.IntegerField()
    goods_price=models.FloatField()
    goods_total_price=models.FloatField()
    order_status=models.IntegerField(default=0) #默认代表未支付
    store_id=models.ForeignKey(to=Login,on_delete=models.CASCADE)

class Cart(models.Model):
    goods_name=models.CharField(max_length=32)
    goods_number=models.IntegerField()
    goods_price=models.FloatField()
    goods_picture=models.CharField(max_length=32)
    goods_total=models.FloatField()
    goods_id=models.IntegerField()
    cart_user=models.IntegerField()
# Create your models here.

