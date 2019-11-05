"""ecom URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from core.views import *
from dashboard.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('', include('allauth.urls')),

    path('facture/<slug:ref>', generate_pdf, name="facture"),

    path('', home, name="home"),
    path('contact/', contact, name="contact"),
    path('orders/', orders, name="user-orders"),
    path('orders-details/<slug:ref>', order_details, name="order-details"),
    path('order-modify/<slug:ref>', order_modify, name="order-modify"),
    path('order-cancel/<slug:ref>', order_cancel, name="order-cancel"),
    path('order-reorder/<slug:ref>', order_reorder, name="order-reorder"),
    path('order-track/<slug:ref>', order_track, name="order-track"),

    path('checkout/', checkout, name="checkout"),
    path('delivery/', delivery, name="delivery"),
    path('update-delivery/<slug:ref>', update_delivery, name="update-delivery"),
    path('payment/', payment, name="payment"),
    path('update-payment/<slug:ref>', update_payment, name="update-payment"),
    path('overview/', overview, name="overview"),
    path('confirmation/', confirmation, name="confirmation"),

    path('profile/', profile, name="user-profile"),
    path('addresses/', addresses, name="user-addresses"),
    path('conditions-vente/', addresses, name="conditions_vente"),
    path('conditions-annulation/', addresses, name="conditions_annulation"),

    path('cart/', cart_view, name="cart"),
    path('addtocart/<slug:slug>', add_to_cart, name="add-to-cart"),
    path('removeformcart/<int:id>/<str:red>', remove_form_cart, name="remove_form_cart"),
    path('increment_item_card/<int:id>/<str:red>', increment_item_card, name="increment_item_card"),
    path('decrement_item_card/<int:id>/<str:red>', decrement_item_card, name="decrement_item_card"),

    path('shop/', shop, name="shop"),
    path('shop/<slug:slug>', shop_by_category, name="shop_by_category"),

    path('details/<slug:slug>', product_details, name="product-details"),
    path('addtofavorite/<slug:slug>', product_details, name="add-to-favorite"),

    path('newsletter/', newsletter, name="newsletter"),
    path('404/', not_found, name="not-found"),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
