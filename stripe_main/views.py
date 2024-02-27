from django.shortcuts import render
import stripe
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from . import models


stripe.api_key = "sk_test_51M5Ej5AOiYw02tQNGQGbO3SGhtmEeEcEb9cVIzcLfOedNl3pJlom5J7BWhnRT2mFqUK0O8L2hQAv4wokmUf7kzqC002m4Jv6OA"


@csrf_exempt
def buy(request):
    '''
    принимает body с ключем items, содержащим массив идентификаторов объектов.

    '''
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            discount = None
            if data['discount'] in \
               [discount.code for discount in models.Discount.objects.all()]:
                discount = models.Discount.get(code=data['discount'])

            tax = None
            if data['tax'] in \
               [tax.id for tax in models.Tax.objects.all()]:
                tax = models.Tax.objects.get(data['tax'])

            order = models.Order.objects.create\
                (amount=0, currency="rur", discount=discount, tax=tax, items=data['items'], payment_intent='')

            intent = stripe.PaymentIntent.create(
              amount=2000,
              currency="usd",
              automatic_payment_methods={"enabled": True},
              setup_future_usage="off_session",
            )

            order.payment_intent = intent['id']
            order.save()

            return JsonResponse({'clientSecret': intent['client_secret']})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return HttpResponse("method not allowed", status=405)


def items(request):
    if "payment_intent" in request.GET:
        order = models.Order.objects.get(payment_intent=
                                 request.GET['payment_intent'])
        order.complete = True
        order.save()

    items = [item for item in models.Item.objects.all()]
    context = {'items': items}
    return render(request, 'stripe_main/items.html', context)


def checkout(request):
    return render(request, 'stripe_main/checkout.html')

