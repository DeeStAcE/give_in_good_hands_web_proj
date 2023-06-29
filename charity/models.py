from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    name = models.CharField(max_length=32)

    def __str__(self):
        return self.name


class Institution(models.Model):
    class Types(models.TextChoices):
        FOUNDATION = 'found', _('Fundacja')
        NONGOVERNMENTAL_ORGANIZATION = 'ngo', _('Organizacja pozarządowa')
        LOCAL_COLLECTION = 'loccol', _('Zbiórka lokalna')

    name = models.CharField(max_length=32)
    description = models.TextField(null=True)
    type = models.CharField(choices=Types.choices, default=Types.FOUNDATION)
    categories = models.ManyToManyField('Category')

    def __str__(self):
        return self.name


class Donation(models.Model):
    quantity = models.SmallIntegerField()
    categories = models.ManyToManyField('Category')
    institution = models.ForeignKey('Institution', on_delete=models.CASCADE)
    address = models.CharField(max_length=64)
    phone_number = models.CharField(max_length=12)
    city = models.CharField(max_length=32)
    zip_code = models.CharField(max_length=6)
    pick_up_date = models.DateField()
    pick_up_time = models.TimeField()
    pick_up_comment = models.TextField(null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, default=None)
