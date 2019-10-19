from django.urls import path

from .views import *

app_name = "db"
urlpatterns = [
    path('', dashboard, name="dashboard"),
    path('orders/', commandes, name="commandes"),
    path('order-details/<slug:ref>', db_order_details, name="order-details"),

    path('products/', products, name="products"),
    path('product-details/<slug:ref>', db_product_details, name="product-details"),
    path('addProduct/', db_add_product, name="add_product"),

    path('categories/', categories, name="categories"),
    path('category-details/<slug:ref>', db_category_details, name="category-details"),
    path('addCategory/', db_add_category, name="add_category"),

    path('attributes/', attributes, name="attributes"),
    path('attribute-details/<slug:ref>', db_attribute_details, name="attribute-details"),
    path('addAttribute/', db_add_attribute, name="add_attribute"),
]
