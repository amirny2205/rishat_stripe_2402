from . import views
from django.urls import path

urlpatterns = [
    path('buy/', views.buy),
    path('items/', views.items),
    path('checkout/', views.checkout),
    path('check_promocode/', views.check_promocode)
]
