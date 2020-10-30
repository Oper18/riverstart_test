# coding: utf-8

from django.db import models


class Category(models.Model):
    name = models.CharField(verbose_name='Category name', max_length=128)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(verbose_name='Product name', max_length=255)
    category = models.ManyToManyField(Category, verbose_name='Category', related_name='products')
    price = models.FloatField(verbose_name='Price')
    publish = models.BooleanField(verbose_name='Publish product', default=False, blank=True)
    delete = models.BooleanField(verbose_name='Deleted product', default=False, blank=True)

    def __str__(self):
        return self.name
