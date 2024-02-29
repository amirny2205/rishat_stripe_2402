from django.db import models

app_label, *_ = __name__.partition('.')


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

    class Meta:
        db_table = app_label + '_items'


class Order(models.Model):
    # stripe принимает оплату в integer и считается как сумма*100
    # т.е. 5000rub даст там 50.00rub то есть 50 рублей
    # оставляю такую же логику для админки
    amount = models.IntegerField()
    currency = models.CharField(choices=currency_choices)
    discounts = models.ManyToManyField('Discount', blank=True)
    taxes = models.ManyToManyField('Tax', blank=True)
    items = models.JSONField(blank=True)
    payment_intent = models.CharField(max_length=255)
    complete = models.BooleanField(default=False)

    def __str__(self):
        return f'({"in" if not self.complete else ""}complete) {self.amount/100}{self.currency}'

    class Meta:
        db_table = app_label + '_orders'


class Discount(models.Model):
    code = models.CharField(max_length=255, primary_key=True)
    amount = models.IntegerField()
    currency = models.CharField(choices=currency_choices)

    def __str__(self):
        return str(self.code) + ' ' + str(self.amount) + self.currency

    class Meta:
        db_table = app_label + '_discounts'


class Tax(models.Model):
    amount = models.IntegerField()
    currency = models.CharField(choices=currency_choices)
    description = models.TextField()

    def __str__(self):
        return str(self.amount) + self.currency + ' ' + self.description[:40]

    class Meta:
        verbose_name_plural = "Taxes"
        db_table = app_label + '_taxes'
