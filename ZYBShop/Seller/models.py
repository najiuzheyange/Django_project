from django.db import models


class GoodsType(models.Model):
    type_label=models.CharField(max_length=32)
    type_description=models.TextField(null=True,blank=True)
    picture=models.ImageField(upload_to="images",default='/static/images/banner01.jpg')

class Login(models.Model):
    email=models.EmailField()
    password=models.CharField(max_length=32)

    username=models.CharField(max_length=32, null=True,blank=True)
    phone_number=models.CharField(max_length=11, null=True,blank=True)
    age=models.IntegerField(null=True, blank=True)
    gender=models.CharField(max_length=32,null=True, blank=True)
    photo=models.ImageField(upload_to="images",null=True, blank=True)
    address=models.TextField(null=True,blank=True)
    user_type=models.IntegerField(default=0) #0代表买家，1代表卖家，2代表管理员




class Goods(models.Model):
    goods_number=models.CharField(max_length=11)
    goods_name=models.CharField(max_length=32)
    goods_price=models.FloatField()
    goods_count=models.IntegerField()
    goods_location=models.CharField(max_length=254)
    goods_safe_date=models.IntegerField()
    goods_pro_time=models.DateField(auto_now=True)
    # goods_description=models.TextField()
    goods_picture=models.ImageField(upload_to="images",default='/static/images/o.jpg')
    goods_status=models.IntegerField(default=1)   #0为下架，1为在售

    goods_type=models.ForeignKey(to=GoodsType,on_delete=models.CASCADE)
    goods_store=models.ForeignKey(to=Login,on_delete=models.CASCADE)


class ValidCode(models.Model):
    code_content = models.CharField(max_length=32)
    code_user = models.EmailField()
    code_time = models.DateTimeField(auto_now=True)
    code_state = models.IntegerField(default=0) #1使用 0未使用









# Create your models here.




