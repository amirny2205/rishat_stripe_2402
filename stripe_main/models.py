from django.db import models

currency_choices = {
    "usd": "usd",
    "rur": "rur"
}


class Item(models.Model):

    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.IntegerField()
    currency = models.CharField(choices=currency_choices)

    def __str__(self):
        return self.name


class Order(models.Model):
    amount = models.IntegerField()
    currency = models.CharField(choices=currency_choices)
    discount = models.ForeignKey(
        'Discount', default=None, blank=True,
        null=True, on_delete=models.PROTECT)
    tax = models.ForeignKey('Tax', blank=True,
                            null=True, on_delete=models.PROTECT)
    items = models.JSONField(blank=True)
    payment_intent = models.CharField(max_length=255)
    complete = models.BooleanField(default=False)

    def __str__(self):
        completeness = "(incomplete)" if not self.complete else "(complete)"
        return completeness + ' ' + str(self.amount) + self.currency


class Discount(models.Model):
    amount = models.IntegerField()
    code = models.CharField(max_length=255)

    def __str__(self):
        return str(self.code)


class Tax(models.Model):
    amount = models.IntegerField()

    def __str__(self):
        return str(self.amount)

    class Meta:
        verbose_name_plural = "Taxes"
