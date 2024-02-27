from django.db import models


class Item(models.Model):
    currency_choices = {
        "usd": "usd",
        "rur": "rur"
    }

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    currency = models.CharField(choices=currency_choices)

    def __str__(self):
        return self.name


class Order(models.Model):
    discount = models.ForeignKey('Discount',
                                 null=True, on_delete=models.SET_NULL)
    tax = models.ForeignKey('Tax', null=True, on_delete=models.PROTECT)
    items = models.ManyToManyField(Item)


class Discount(models.Model):
    amount = models.IntegerField()

    def __str__(self):
        return str(self.amount)


class Tax(models.Model):
    amount = models.IntegerField()

    def __str__(self):
        return str(self.amount)
