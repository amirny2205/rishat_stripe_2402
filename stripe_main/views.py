from django.shortcuts import render
import stripe
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from . import models
import traceback
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.http import require_POST
from django.conf import settings


stripe.api_key = settings.STRIPE_API_KEY

minimum_amounts = {'usd': 1, 'rub': 50}


@csrf_exempt
@require_POST
def buy(request):
    '''
    принимает body с ключем items, содержащим массив идентификаторов объектов.
    создаёт PayentIntent, создаёт order, но его подтвердит вебхук
    выдаёт :
    - clientSecret для оплаты
    - remaining_data, оплата происходит по группам по признаку валюты. Выранные но неоплаченные вещи возвращаются на фронт, и создаётся новый запрос.
    - order_data для отображения того, что сейчас собирается купить пользователь
    '''
    try:
        data = json.loads(request.body)

        # сначала группируем items по аттрибуту currency
        # на выходе словарь
        # {'usd': {'2': [obj, quantity]}, 'rub': ..., 'other': ...,  ...}
        items = {}
        # все items,
        # они будут впоследствии распилены по признаку валюты на "сейчас" и "потом"
        for element_id in data['items']:
            current_item = models.Item.objects.get(id=element_id)
            if current_item.currency not in items:
                items[current_item.currency] = {}
            items[current_item.currency][element_id] =\
                [current_item, data['items'][element_id]]

        currency = list(items)[0]
        items_now = items[currency]

        items_remaining = {}
        items_keys_remaining = list(items)
        items_keys_remaining.remove(currency)
        for tmp_currency in items_keys_remaining:
            items_remaining.update(items[tmp_currency])

        discounts = models.Discount.objects\
            .filter(code__in=data['discounts'])\
            .filter(currency=currency)

        taxes = models.Tax.objects\
            .filter(id__in=data['taxes'])\
            .filter(currency=currency)


        # обыкновенно поведение Tax выставлялось бы в кастомной админской панели,
        # для тестового задания оставлю "всегда использова первый налог, если есть"

        if not taxes:
            modeltaxes = models.Tax.objects.filter(currency=currency)
            taxes = [modeltaxes[0]] if modeltaxes else []
        # временная логика налога(Tax) кончается здесь

        amount = 0
        for item in items_now:
            amount += items_now[item][0].price * int(items_now[item][1])

        for discount in discounts:
            if discount.currency == currency:
                amount -= discount.amount

        for tax in taxes:
            if tax.currency == currency:
                amount += tax.amount

        amount = max(minimum_amounts[currency], amount)
        # stripe принимает оплату в integer и считается как сумма*100
        # т.е. 5000rub даст там 50.00rub то есть 50 рублей
        # оставляю такую же логику для админки
        amount *= 100

        intent = stripe.PaymentIntent.create(
          amount=amount,
          currency=currency,
          automatic_payment_methods={"enabled": True},
          setup_future_usage="off_session",
        )

        order = models.Order.objects.create\
            (amount=amount, currency=currency,
             items={k: v for k, v in zip(
                 [item_id for item_id in items_now],
                 [items_now[item][1] for item in items_now])},
             payment_intent=intent['id'])
        order.taxes.set(taxes)
        order.discounts.set(discounts)

        order_data = {}
        order_data = {
            'amount': amount, 'currency': currency,
            'discounts': [], 'items': [], 'taxes': []}
        for item in items_now:
            order_data['items'].append([items_now[item][0].name, items_now[item][0].price, items_now[item][1]])
        for discount in discounts:
            order_data['discounts'].append([discount.code, discount.amount])
        for tax in taxes:
            order_data['taxes'].append([tax.amount, tax.description])

        remaining_data = []
        if items_remaining:
            remaining_data = data.copy()
            remaining_data.update({'items': {k: v for k, v in zip([item_id for item_id in items_remaining], [items_remaining[item][1] for item in items_remaining])}})
        return JsonResponse(
            {'clientSecret': intent['client_secret'],
             'remaining_data': json.dumps(remaining_data),
             'order_data': json.dumps(order_data)})

    except Exception as e:
        print(traceback.format_exc())
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
@require_POST
def check_promocode(request):
    try:
        discount = models.Discount.objects.get(code=json.loads(request.body)['promocode'])
        return HttpResponse(json.dumps({'result': 'promocode found', 'discount': [discount.code, discount.amount, discount.currency]}), content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'result': 'promocode not found'}), content_type="application/json")
        return HttpResponse('promocode not found')
    except Exception:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'result': 'internal server error'}), status=500, content_type="application/json")


def checkout(request):
    return render(request, 'stripe_main/checkout.html',
                  context={'stripe_secret_api_key': settings.STRIPE_SECRET_API_KEY,
                           'return_url': settings.CHECKOUT_RETURN_URL})


def payment_submitted(request):
    return render(request, 'stripe_main/payment_submitted.html',
                  context={'stripe_secret_api_key': settings.STRIPE_SECRET_API_KEY})


@csrf_exempt
@require_POST
def webhook(request):
    try:
        event = json.loads(request.body)
    except json.decoder.JSONDecodeError as e:
        print('⚠️  Webhook error while parsing basic request.' + str(e))
        return HttpResponse('Webhook error while parsing basic request. except json.decoder.JSONDecodeError branch have executed.', status=400)
    except Exception:
        print(traceback.format_exc())
        return HttpResponse('internal server error', status=500)
    # Handle the event
    if event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        try:
            order = models.Order.objects.get(payment_intent=payment_intent['id'])
            order.complete = True
            order.save()
        except Exception:
            print(traceback.format_exc())
            # здесь должна быть логика логгирования ошибок
        # print('Payment for {} succeeded'.format(payment_intent['amount']))
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
    # else:
        # Unexpected event type
        # print('Unhandled event type {}'.format(event['type']))

    return JsonResponse({'success': True})


def items(request):
    context = {'items': models.Item.objects.all()}
    return render(request, 'stripe_main/items.html', context)
