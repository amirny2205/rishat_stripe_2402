from django.db import models

currency_choices = {
    "usd": "usd",
    "rub": "rub"
}


class Item(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    currency = models.CharField(choices=currency_choices)

    def __str__(self):
        return self.name


class Order(models.Model):
    # stripe принимает оплату в integer и считается как сумма*100
    # т.е. 5000rub даст там 50.00rub то есть 50 рублей
    # оставляю такую же логику для админки
    amount = models.IntegerField()
    currency = models.CharField(choices=currency_choices)
    discounts = models.ManyToManyField('Discount')
    taxes = models.ManyToManyField('Tax')
    items = models.JSONField(blank=True)
    payment_intent = models.CharField(max_length=255)
    complete = models.BooleanField(default=False)

    def __str__(self):
        completeness = "(incomplete)" if not self.complete else "(complete)"
        return completeness + ' ' + str(self.amount/100) + self.currency


class Discount(models.Model):
    amount = models.IntegerField()
    currency = models.CharField(choices=currency_choices)
    code = models.CharField(max_length=255)

    def __str__(self):
        return str(self.code) + ' ' + str(self.amount) + self.currency


class Tax(models.Model):
    amount = models.IntegerField()
    currency = models.CharField(choices=currency_choices)
    description = models.TextField()

    def __str__(self):
        return str(self.amount) + self.currency + ' ' + self.description[:40]

    class Meta:
        verbose_name_plural = "Taxes"
