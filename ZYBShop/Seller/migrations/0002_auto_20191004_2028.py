# Generated by Django 2.1.8 on 2019-10-04 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Seller', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='goods',
            name='goods_picture',
            field=models.ImageField(default='/static/seller/images/kb.jpg', upload_to='images'),
        ),
        migrations.AlterField(
            model_name='goodstype',
            name='picture',
            field=models.ImageField(default='/static/seller/images/banner01.jpg', upload_to='images'),
        ),
    ]