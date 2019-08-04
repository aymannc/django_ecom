import random
import string
from urllib.parse import quote_plus

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import CouponForm, MessageForm, AddressForm, ContactForm
from .models import *


def random_ref():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def home(req):
    banners = Banner.objects.filter(is_active=True)
    categories = Category.objects.filter(is_featured=True)
    products = Product.objects.filter(is_featured=True)

    context = {
        'categories': categories,
        'banners': banners,
        'products': products
    }
    return render(req, "index.html", context)


def product_details(req, slug):
    product = get_object_or_404(Product, slug=slug)
    context = {
        "product": product,
        "share_string": quote_plus(product.product_description)
    }
    return render(req, "detail.html", context)


def shop(req):
    product_list = Product.objects.all().order_by('-last_modified')
    paginator = Paginator(product_list, 9)
    page_request_var = 'page'
    page = req.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'count': paginator.count,
        'start': paginated_queryset.start_index,
        'end': paginated_queryset.end_index,
        'page_request_var': page_request_var,
    }
    return render(req, 'shop.html', context)


def shop_by_category(req, slug):
    category = Category.objects.filter(slug=slug)
    context = {
        "category": category,
    }
    return render(req, "shop.html", context)


def not_found(req):
    return render(req, "404.html", {})


def remove_form_cart(req, id):
    order_item = OrderItem.objects.get(id=id)
    order = Order.objects.get(id=order_item.order.id)
    order_item.delete()
    count = order.items.count()

    if not count:
        try:
            if order.id == req.session['cart']:
                del req.session['cart']
                req.session.modified = True
        except:
            pass
        order.delete()
        messages.success(req, "Card is Empty ")
        return redirect("home")

    messages.success(req, "Item deleted successfully")
    return redirect("cart")


def cart_view(req):
    order = None
    if req.user.is_authenticated:
        try:
            order_id = req.session['cart']
        except:
            order_id = None

        order_qs = Order.objects.filter(user=req.user, ordered=False)
        if order_qs.exists():
            if order_id:
                order_qs[0].user = None
                print("user", order_qs[0].user)
                # order_qs[0].save()
                print(" user_id", order_qs[0].user_id)
                order = Order.objects.get(id=order_id)
                order.user = req.user
                order.save()
            else:
                order = order_qs[0]
        else:
            order = None
            if order_id:
                order = Order.objects.get(id=order_id)
                order.user = req.user
                order.save()
            messages.warning(req, "You do not have an active order ")

    else:
        try:
            order = Order.objects.get(id=req.session['cart'])
        except Order.DoesNotExist:
            messages.warning(req, "You do not have an active order ")
            order = None
        except KeyError:
            messages.warning(req, "Order unavailable or deleted ")
    try:
        count = order.items.count()
    except:
        count = 0

    if req.method == "POST":
        coupon = CouponForm(req.POST or None)
        message = MessageForm(req.POST or None)
        if coupon.is_valid():
            if coupon.cleaned_data.get('code'):
                try:
                    if order.coupon.code == coupon.cleaned_data['code']:
                        messages.warning(req, "You allready added this coupon ")
                        return redirect("cart")
                except:
                    pass
                try:
                    coupon = Coupon.objects.get(code=coupon.cleaned_data['code'], expire_date__gte=timezone.now())
                    if order:
                        order.coupon = coupon
                        order.save()
                        messages.success(req, "Coupon added succesufly ")
                    else:
                        messages.warning(req, "You do not have an active order ")
                except:
                    messages.warning(req, "Coupon is None Valide or expired !")

            else:
                messages.warning(req, "Non Valid Coupon !")
        elif message.is_valid():
            if message.cleaned_data.get('message'):
                try:
                    order = Order.objects.get(user=req.user, ordered=False)
                    order.message = message.cleaned_data["message"]
                    order.save()
                except:
                    messages.error(req, "Error getting your order")
                messages.success(req, "Instructions added")
            return redirect("checkout")

        else:
            messages.warning(req, "Error getting the Coupon or Message")

        return redirect("cart")

    context = {
        "order": order,
        "order_count": count,
        "coupon": CouponForm(),
        "message": MessageForm(),
    }
    return render(req, "cart.html", context)


def add_to_cart(req, slug):
    item = get_object_or_404(Product, slug=slug)
    order_item = OrderItem(
        product=item,
        quantity=req.GET.get('quantity', 1)
    )
    if req.user.is_authenticated:
        order_qs = Order.objects.filter(user=req.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
            order_item_qs = order.items.filter(product__slug=item.slug)
            if order_item_qs.exists():
                order_item = order_item_qs[0]
                quantity = int(req.GET.get('quantity', 1))
                order_item.quantity += quantity
                order_item.save()
                messages.info(req, "This item quantity was updated.")
            else:
                order_item.order = order
                order_item.save()
                messages.info(req, "This item was added to your cart.")

        else:
            order = Order.objects.create(
                user=req.user,
                # ref_code=f"{req.user}-{slug}-{timezone.now()}"
                ref_code=random_ref()
            )
            order_item.order = order
            order_item.save()
            order.save()
            messages.info(req, "This item was added to your cart.")

    else:
        try:
            order_id = req.session['cart']
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                messages.info(req, "This order is deleted or not available")
                return redirect("cart")
            order_item_qs = order.items.filter(product__slug=item.slug)
            if order_item_qs.exists():
                order_item = order_item_qs[0]
                quantity = int(req.GET.get('quantity', 1))
                order_item.quantity += quantity
                order_item.save()
                messages.info(req, "This item quantity was updated.")
            else:
                order_item.order = order
                order_item.save()
                messages.info(req, "This item was added to your cart.")
        except KeyError:
            order = Order.objects.create(
                ref_code=random_ref()
            )
            order_item.order = order
            order_item.save()
            order.save()
            req.session['cart'] = order.id
            messages.info(req, "This item was added to your cart.")
    return redirect("cart")


def increment_item_card(req, id):
    item_card = OrderItem.objects.get(id=id)
    item_card.quantity += 1
    item_card.save()
    return redirect("cart")


def decrement_item_card(req, id):
    item_card = OrderItem.objects.get(id=id)
    item_card.quantity -= 1
    item_card.save()
    if not item_card.quantity:
        remove_form_cart(req, id)
    return redirect("cart")


def contact(req):
    form = ContactForm()
    if req.method == "POST":
        form = ContactForm(req.POST or None)
        if form.is_valid():
            form.save()
            messages.success(req, "Message sent")
        else:
            messages.error(req, "Error while submitting the form")

    context = {
        "form": form
    }
    return render(req, "contact.html", context)


def blog(req):
    return render(req, "blog.html", {})


def login(req):
    return render(req, "customer-login.html", {})


@login_required
def orders(req):
    user = req.user
    orders = Order.objects.filter(user=req.user, ordered=True)
    context = {
        "user": user,
        "orders": orders
    }
    return render(req, "customer-orders.html", context)


@login_required
def order_details(req, ref):
    try:
        order = Order.objects.get(ref_code=ref)
    except:
        messages.error(req, "Non valid reference code ")
        return redirect("user-orders")
    context = {
        "order": order,
    }
    return render(req, "customer-order.html", context)


@login_required
def profile(req):
    return render(req, "customer-account.html", {})


@login_required
def addresses(req):
    return render(req, "customer-addresses.html", {})


@login_required
def checkout(req):
    try:
        order = Order.objects.get(user=req.user, ordered=False)
    except:
        messages.error(req, "Non Valid order")
        return redirect("home")
    try:
        form = AddressForm(instance=order.shipping_address)
    except:
        form = AddressForm()
    if req.method == "POST":
        form = AddressForm(req.POST or None)
        if form.is_valid():
            address = Address(**form.cleaned_data)
            address.user = req.user
            address.save()
            order.shipping_address = address
            order.billing_address = address
            order.save()
            messages.success(req, "Address Saved")
            return redirect("delivery")
        else:
            messages.error(req, "Errors in Form")

    context = {
        "form": form,
    }
    return render(req, "checkout1.html", context)


@login_required
def delivery(req):
    try:
        order = Order.objects.get(user=req.user, ordered=False)
        if not order.shipping_address:
            messages.error(req, "You Need a shipping address")
            return redirect("address")
    except:
        messages.error(req, "Non Valid order")
        return redirect("home")

    if req.method == "POST":
        try:
            method = DeliveryMethod.objects.get(id=req.POST['option_id'])
            order.delivery_method = method
            order.save()
            return redirect("payment")
        except:
            messages.error(req, "Non Valide Method")

    user_method = order.delivery_method
    if user_method:
        methods = DeliveryMethod.objects.exclude(id=user_method.id)
    else:
        methods = DeliveryMethod.objects.all()
    context = {
        "methods": methods,
        "user_method": user_method
    }
    return render(req, "checkout2.html", context)


@login_required
def payment(req):
    payment_methods = None
    try:
        order = Order.objects.get(user=req.user, ordered=False)
        if not order.shipping_address:
            messages.error(req, "You Need a shipping address")
            return redirect("address")
        if not order.delivery_method:
            messages.error(req, "You Need a delivery method")
            return redirect("delivery")
    except:
        messages.error(req, "Non Valid order !")
        return redirect("home")

    if req.method == "POST":
        if req.POST.get('option_id'):
            try:
                payment_option = PaymentOptions.objects.get(id=req.POST['option_id'])
                order.payment_option = payment_option
                order.save()
                payment_methods = payment_option.payment_methods.all()
                return render(req, "checkout3.html", {"payment_methods": payment_methods})
            except:
                messages.error(req, "Non Valid option")
        elif req.POST.get('e2option_id'):
            try:
                payment_method = PaymentMethod.objects.get(id=req.POST['e2option_id'])
                order.payment_method = payment_method
                order.save()
                return redirect("overview")
            except:
                messages.error(req, "Non Valid payment option")

    payment_option = order.payment_option

    if payment_option:
        add = False
        for v in order.delivery_method.payment_options.all():
            if v.id == payment_option.id:
                add = True
        if not add:
            payment_option = None

    if payment_option:
        payment_options = order.delivery_method.payment_options.exclude(id=payment_option.id)
    else:
        payment_options = order.delivery_method.payment_options.all()

    context = {
        "payment_options": payment_options,
        "payment_option": payment_option,
    }
    return render(req, "checkout3.html", context)


@login_required
def overview(req):
    try:
        order = Order.objects.get(user=req.user, ordered=False)
        if not order.shipping_address:
            messages.error(req, "You Need a shipping address")
            return redirect("address")
        if not order.delivery_method:
            messages.error(req, "You Need a delivery method")
            return redirect("delivery")
        if not order.payment_option or not order.payment_method:
            messages.error(req, "You Need payment options")
            return redirect("payment")
    except:
        messages.error(req, "Non Valid order !")
        return redirect("home")

    context = {
        "order": order,
    }
    return render(req, "checkout4.html", context)


@login_required
def confirmation(req):
    try:
        order = Order.objects.get(user=req.user, ordered=False)
        if not order.shipping_address:
            messages.error(req, "You Need a shipping address")
            return redirect("address")
        if not order.delivery_method:
            messages.error(req, "You Need a delivery method")
            return redirect("delivery")
        if not order.payment_option or not order.payment_method:
            messages.error(req, "You Need payment options")
            return redirect("payment")
    except:
        messages.error(req, "Non Valid order !")
        return redirect("home")
    try:
        order.ordered = True
        order.ordered_date = timezone.now()
        order.order_status = "ON HOLD"
        order.save()
    except:
        messages.error(req, "Error while saving your order")
        return redirect("overview")
    context = {
        "user": req.user,
    }
    return render(req, "checkout5.html", context)
