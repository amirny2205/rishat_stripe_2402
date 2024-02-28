from django.shortcuts import render
import stripe
from django.http import HttpResponse, JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from . import models
from django.http import HttpResponseRedirect
import traceback
from django.core.exceptions import ObjectDoesNotExist

stripe.api_key = "sk_test_51M5Ej5AOiYw02tQNGQGbO3SGhtmEeEcEb9cVIzcLfOedNl3pJlom5J7BWhnRT2mFqUK0O8L2hQAv4wokmUf7kzqC002m4Jv6OA"

minimum_amounts = { 'usd': 1, 'rub': 50 }


@csrf_exempt
def buy(request):
    '''
    принимает body с ключем items, содержащим массив идентификаторов объектов.

    '''
    if request.method == "POST":
        try:
            data = json.loads(request.body)

            # сначала группируем items по аттрибуту currency
            # на выходе словарь
            # {'usd': {'2': [obj, quantity]}, 'rub': ..., 'other': ...,  ...}
            items = {}
            for element_id in data['items']:
                current_item = models.Item.objects.get(id=element_id)
                if current_item.currency not in items:
                    items[current_item.currency] = {}
                items[current_item.currency][element_id] =\
                    [current_item ,data['items'][element_id]]


            currency = list(items)[0]
            items_now = items[currency]

            items_remaining = {}
            items_keys_remaining = list(items)
            items_keys_remaining.remove(currency)
            for tmp_currency in items_keys_remaining:
                items_remaining.update(items[tmp_currency])


            discounts = None
            if 'discounts' in data and data['discounts']:
                discounts = []
                for discount_code in data['discounts']:
                    discount = models.Discount.objects.get(code=discount_code)
                    if discount.currency == currency:
                        discounts.append(discount)

            taxes = None
            if 'taxes' in data and data['taxes']:
                taxes = []
                for tax_id in data['taxes']:
                    tax = models.Tax.objects.get(id=tax_id)
                    if tax.currency == currency:
                        taxes.append(tax)

            # обыкновенно поведение Tax выставлялось бы в кастомной админской панели,
            # для тестового задания оставлю "всегда использова первый налог, если есть"
            
            if not taxes:
                modeltaxes = models.Tax.objects.filter(currency=currency)
                taxes = [modeltaxes[0]] if modeltaxes else []
            # временная логика налога(Tax) кончается здесь

            amount = 0
            for item in items_now:
                amount += items_now[item][0].price * items_now[item][1]

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

            order = models.Order.objects.create\
                (amount=amount, currency=currency,
                 items={k: v for k, v in zip(
                     [item_id for item_id in items_now],
                     [items_now[item][1] for item in items_now])},
                 payment_intent='')

            order.taxes.set(taxes)
            #    models.Tax.objects.filter(id__in=[tax.id for tax in taxes]))
            order.discounts.set(discounts)
            

            intent = stripe.PaymentIntent.create(
              amount=amount,
              currency=currency,
              automatic_payment_methods={"enabled": True},
              setup_future_usage="off_session",
            )

            order.payment_intent = intent['id']
            order.save()

            order_data = {}
            order_data['amount'] = amount
            order_data['currency'] = currency
            order_data['discounts'] = []
            order_data['items'] = []
            order_data['taxes'] = []
            for item in items_now:
                order_data['items'].append([items_now[item][0].name, items_now[item][0].price, items_now[item][1]])
            for discount in discounts:
                order_data['discounts'].append([discount.code, discount.amount])
            for tax in taxes:
                order_data['taxes'].append([tax.amount, tax.description])

            if items_remaining:
                remaining_data = data.copy()
                remaining_data.update({'items': {k: v for k, v in zip([item_id for item_id in items_remaining], [items_remaining[item][1] for item in items_remaining])}})
                return JsonResponse(
                    {'clientSecret': intent['client_secret'],
                     'remaining_data': json.dumps(remaining_data),
                     'order_data': json.dumps(order_data)})
            return JsonResponse(
                {'clientSecret': intent['client_secret'],
                 'order_data': json.dumps(order_data)})


        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return HttpResponse("method not allowed", status=405)


def items(request):
    if "payment_intent" in request.GET:
        order = models.Order.objects.get(payment_intent=
                                         request.GET['payment_intent'])
        order.complete = True
        order.save()

    remaining_items = request.GET['remaining_items'] if 'remaining_items'\
        in request.GET else None
    
    if remaining_items:
        remaining_items_str = json.dumps(remaining_items)
        discounts_str = '' if 'discounts' \
            not in request.GET else '&discounts=' + request.GET['discounts']
        
        return HttpResponseRedirect('/checkout/' + '?' +
                                    'items=' + remaining_items_str +
                                    discounts_str)

    items = [item for item in models.Item.objects.all()]

    context = {'items': items, 'remaining_items': remaining_items}
    return render(request, 'stripe_main/items.html', context)


def checkout(request):
    return render(request, 'stripe_main/checkout.html')


@csrf_exempt
def check_promocode(request):
    try:
        discount = models.Discount.objects.get(code=json.loads(request.body)['promocode'])
        return HttpResponse(json.dumps({'result': 'promocode found', 'discount': [discount.code, discount.amount, discount.currency]}), content_type="application/json")
    except ObjectDoesNotExist:
        return HttpResponse(json.dumps({'result': 'promocode not found'}), content_type="application/json")
        return HttpResponse('promocode not found')
    except Exception as e:
        print(traceback.format_exc())
        return HttpResponse(json.dumps({'result': 'internal server error'}), status=500, content_type="application/json")
    
