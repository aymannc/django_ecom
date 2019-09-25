from django.urls import path

from .views import *

app_name = "db"
urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('commandes/', commandes, name="commandes"),
    path('order-details/<slug:ref>', db_order_details, name="order-details"),
]
