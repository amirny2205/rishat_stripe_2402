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
            intent = stripe.PaymentIntent.create(
              amount=2000,
              currency="usd",
              automatic_payment_methods={"enabled": True},
              setup_future_usage="off_session",
            )
            return JsonResponse({'clientSecret': intent['client_secret']})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        raise HttpResponse("method not allowed", status=405)


def items(request):
    items = [item for item in models.Item.objects.all()]
    context = {'items': items}
    return render(request, 'stripe_main/items.html', context)
