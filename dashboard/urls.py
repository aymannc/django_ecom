from django.urls import path

from .views import *

app_name = "db"
urlpatterns = [
    path('', dashboard, name="dashboard"),

    path('orders/', commandes, name="commandes"),
    path('order-details/<slug:ref>', db_order_details, name="order-details"),

    path('users/', users, name="users"),
    path('user-details/<slug:ref>', db_user_details, name="user-details"),
    path('addUser/', db_add_user, name="add_user"),
    path('deleteUser/<slug:ref>', db_delete_user, name="deleteUser"),

    path('products/', products, name="products"),
    path('product-details/<slug:ref>', db_product_details, name="product-details"),
    path('addProduct/', db_add_product, name="add_product"),
    path('deleteProduct/<slug:ref>', db_delete_product, name="deleteProduct"),

    path('categories/', categories, name="categories"),
    path('category-details/<slug:ref>', db_category_details, name="category-details"),
    path('addCategory/', db_add_category, name="add_category"),

    path('attributes/', attributes, name="attributes"),
    path('attribute-details/<slug:ref>', db_attribute_details, name="attribute-details"),
    path('addAttribute/', db_add_attribute, name="add_attribute"),

    path('analytique/', analytique, name="analytique"),

    path('messages/', contacts, name="messages"),
    path('message-details/<slug:ref>', db_messages_details, name="message-details"),
    path('deleteMessage/<slug:ref>', db_delete_message, name="deleteMessage"),

    path('newsletter/', newsletter, name="newsletter"),
    path('add-newsletter/', add_newsletter, name="add-newsletter"),
    path('newsletter-details/<slug:ref>', newsletter_details, name="newsletter-details"),
    path('send-newsletter/<slug:ref>', send_newsletter, name="send-newsletter"),
    path('delete-newsletter/<slug:ref>', del_newsletter, name="delete-newsletter"),

    path('newsletter-emails/', newsletter_emails, name="newsletter-emails"),
    path('delete-newsletter-email/<slug:ref>', del_newsletter_email, name="delete-newsletter-email"),
]
