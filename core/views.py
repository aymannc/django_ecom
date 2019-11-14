import random
from urllib.parse import quote_plus

from allauth.account.forms import ChangePasswordForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import FieldDoesNotExist, Q
from django.forms.models import model_to_dict
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import *
from .models import *


def random_ref():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


def home(req):
    banners = Banner.objects.filter(is_active=True)
    categories = Category.objects.filter(is_featured=True)
    featured_products = Product.objects.filter(is_featured=True)
    context = {
        'categories': categories,
        'banners': banners,
        'featured_products': featured_products
    }
    return render(req, "index.html", context)


def product_details(req, slug):
    product = get_object_or_404(Product, slug=slug)
    category = None
    for cat in product.product_categorie.all():
        if cat.parent_category:
            category = cat
            break
    context = {
        "product_available": product.product_quantity_available,
        "product": product,
        "category": category,
        "share_string": quote_plus(product.product_description)
    }
    return render(req, "detail.html", context)


def shop(req):
    categories = Category.objects.filter(parent_category=None)
    valid = False
    value = None
    if req.POST.get("order"):
        value = req.POST["order"]
        try:
            Product._meta.get_field(value)
            valid = True
        except FieldDoesNotExist as e:
            print("Exception shop", e)
            try:
                Product._meta.get_field(value[1:])
                valid = True
            except FieldDoesNotExist as e:
                print("Exception shop", e)
                messages.error(req, "Non valid selector")
    selected = "-date_added"
    if valid:
        selected = value
    product_list = Product.objects.all().order_by(selected)
    search = req.GET.get('search')
    if search:
        product_list = product_list.filter(
            Q(product_name__icontains=search) |
            Q(product_name__icontains=search) |
            Q(product_description__icontains=search) |
            Q(product_categorie__name__icontains=search) |
            Q(tags__tag__icontains=search)
        ).distinct()

    paginator = Paginator(product_list, 9)
    page_request_var = 'page'
    page = req.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger as e:
        print("Exception shop", e)
        paginated_queryset = paginator.page(1)
    except EmptyPage as e:
        print("Exception shop", e)
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'selected': selected,
        'queryset': paginated_queryset,
        'count': paginator.count,
        'start': paginated_queryset.start_index,
        'end': paginated_queryset.end_index,
        'page_request_var': page_request_var,
    }
    return render(req, 'shop.html', context)


def shop_by_category(req, slug):
    try:
        category = Category.objects.get(slug=slug)
    except Exception as e:
        print("Exception shop_by_category", e)
        messages.error(req, "Non Valid Category")
        return redirect("shop")

    categories = Category.objects.filter(parent_category=None)
    valid = False
    value = None
    if req.POST.get("order"):
        value = req.POST["order"]
        try:
            Product._meta.get_field(value)
            valid = True
        except FieldDoesNotExist as e:
            print("FieldDoesNotExist1 shop_by_category", e)
            try:
                Product._meta.get_field(value[1:])
                valid = True
            except FieldDoesNotExist as e:
                print("FieldDoesNotExist2 shop_by_category", e)
                messages.error(req, "Non valid selector")
    selected = "-date_added"
    if valid:
        selected = value
    if category.parent_category:
        product_list = category.products.order_by(selected)
    else:
        product_list = category.get_parent_products()

    paginator = Paginator(product_list, 9)
    page_request_var = 'page'
    page = req.GET.get(page_request_var)
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger as e:
        print("PageNotAnInteger shop_by_category", e)
        paginated_queryset = paginator.page(1)
    except EmptyPage as e:
        print("EmptyPage shop_by_category", e)
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'categories': categories,
        'selected': selected,
        'queryset': paginated_queryset,
        'count': paginator.count,
        'start': paginated_queryset.start_index,
        'end': paginated_queryset.end_index,
        'page_request_var': page_request_var,
    }
    return render(req, 'shop.html', context)


def not_found(req):
    return render(req, "404.html", {})


def remove_form_cart(req, id, red):
    try:
        order_item = OrderItem.objects.get(id=id)
    except Exception as e:
        print("Exception remove_form_cart", e)
        return redirect("user-orders")
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
        if not order.ordered:
            messages.success(req, "Non valide commande ")
            order.delete()
            return redirect("home")
        else:
            order.delete()

    messages.success(req, "Item deleted successfully")
    print("this shit ", red + " " + order.ref_code)
    return redirect(red, ref=order.ref_code)


def cart_view(req):
    order = None
    if req.user.is_authenticated:
        try:
            order_id = req.session['cart']
            print("req.session['cart']", req.session['cart'])
        except Exception as e:
            print("Exception cart_view", e)
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
            messages.warning(req, "Vous n'avez pas de commande active ")

    else:
        try:
            order = Order.objects.get(id=req.session['cart'])
        except Order.DoesNotExist as e:
            print("DoesNotExist cart_view", e)
            messages.warning(req, "Vous n'avez pas de commande active ")
            order = None
        except KeyError as e:
            print("KeyError cart_view", e)
            messages.warning(req, "Commande indisponible ou supprimée ")
    try:
        count = order.items.count()
    except Exception as e:
        print("Exception cart_view", e)
        count = 0

    if req.method == "POST":
        coupon = CouponForm(req.POST or None)
        message = MessageForm(req.POST or None)
        if coupon.is_valid():
            if coupon.cleaned_data.get('code'):
                if order.coupon:
                    if order.coupon.code == coupon.cleaned_data['code']:
                        messages.warning(req, "Vous avez déjà ajouté ce coupon ")
                        return redirect("cart")
                try:
                    coupon = Coupon.objects.get(code=coupon.cleaned_data['code'], expire_date__gte=timezone.now())
                    if order:
                        order.coupon = coupon
                        order.save()
                        messages.success(req, "Coupon ajouté avec succès ")
                    else:
                        messages.warning(req, "Vous n'avez pas de commande active ")
                except Exception as e:
                    print("Exception cart_view", e)
                    messages.warning(req, "Le coupon n'est pas valide ou a expiré !")
            else:
                messages.warning(req, "Coupon non valide !")
        elif message.is_valid():
            if message.cleaned_data.get('message'):
                try:
                    order.message = message.cleaned_data["message"]
                    order.save()
                except Exception as e:
                    print("Exception cart_view", e)
                    messages.error(req, "Erreur lors de l'obtention de votre commande")
                messages.success(req, "Instructions added")
            return redirect("checkout")
        elif not message.is_valid():
            messages.warning(req, "Erreur lors de la réception du message")
        else:
            messages.warning(req, "Erreur lors de la réception du coupon ")

        return redirect("cart")

    context = {
        "order": order,
        "order_count": count,
        "coupon": CouponForm(),
        "message": MessageForm(),
    }
    return render(req, "cart.html", context)


def add_to_cart(req, slug):
    # TODO : check for quantity + view quantity error and disable order button
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
                if order_item.quantity + quantity < order_item.product.product_quantity_available:
                    order_item.quantity += quantity
                    order_item.save()
                    messages.info(req, "Quantité mise à jour.")
                else:
                    messages.error(req, "Error : rupture de stock")
            else:
                order_item.order = order
                order_item.save()
                messages.info(req, "Une article a été ajouté à votre panier.")

        else:
            order = Order.objects.create(
                user=req.user,
                # ref_code=f"{req.user}-{slug}-{timezone.now()}"
                ref_code=random_ref()
            )
            order_item.order = order
            order_item.save()
            order.save()
            messages.info(req, "Une article a été ajouté à votre panier.")

    else:
        try:
            order_id = req.session['cart']
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist as e:
                print("DoesNotExist add_to_cart", e)
                messages.info(req, "This order is deleted or not available")
                return redirect("cart")
            order_item_qs = order.items.filter(product__slug=item.slug)
            if order_item_qs.exists():
                order_item = order_item_qs[0]
                quantity = int(req.GET.get('quantity', 1))
                if quantity < order_item.product.product_quantity_available:
                    order_item.quantity += quantity
                    order_item.save()
                    messages.info(req, "Quantité mise à jour.")
                else:
                    messages.error(req, "Error : rupture de stock")
            else:
                order_item.order = order
                order_item.save()
                messages.info(req, "Une article a été ajouté à votre panier.")
        except KeyError as e:
            print("DoesNotExist add_to_cart", e)
            order = Order.objects.create(
                ref_code=random_ref()
            )
            order_item.order = order
            order_item.save()
            order.save()
            req.session['cart'] = order.id
            messages.info(req, "Une article a été ajouté à votre panier.")
    return redirect("cart")


def increment_item_card(req, id, red):
    item_card = OrderItem.objects.get(id=id)
    if item_card.product.product_quantity_available > item_card.quantity:
        item_card.quantity += 1
        item_card.save()
        messages.info(req, "Quantité mise à jour.")
    else:
        messages.error(req, "Error : rupture de stock")
    try:
        return redirect(red, ref=item_card.order.ref_code)
    except Exception as e:
        print("Exception increment_item_card", e)
        return redirect(red)


def decrement_item_card(req, id, red):
    item_card = OrderItem.objects.get(id=id)
    ref_code = item_card.order.ref_code
    item_card.quantity -= 1
    item_card.save()
    if not item_card.quantity:
        remove_form_cart(req, id, red)
    try:
        return redirect(red, ref=ref_code)
    except Exception as e:
        print("Exception decrement_item_card", e)
        return redirect(red)


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
        order = Order.objects.get(ref_code=ref, user=req.user)
    except Exception as e:
        print("Exception order_details", e)
        messages.error(req, "Non valid reference ou pas d'autorisation ")
        return redirect("user-orders")
    context = {
        "order": order,
    }
    return render(req, "customer-order.html", context)


@login_required
def order_track(req, ref):
    try:
        order = Order.objects.get(ref_code=ref)
    except Exception as e:
        print("Exception order_track", e)
        messages.error(req, "Référence de commande non valide ")
        return redirect("user-orders")
    context = {
        "order": order,
    }
    return render(req, "track-order.html", context)


@login_required
def order_cancel(req, ref):
    try:
        order = Order.objects.get(ref_code=ref)
        order.order_status = "CANCELED"
        order.save()
    except Exception as e:
        print("Exception order_cancel", e)
        messages.error(req, "Référence de commande non valide ")
        return redirect("user-orders")
    return redirect("user-orders")


@login_required
def order_reorder(req, ref):
    try:
        order = Order.objects.get(ref_code=ref)
        new_one = Order.objects.create(
            user=order.user,
            ref_code=random_ref(),
            message=order.message,
            delivery_method=order.delivery_method,
            payment_option=order.payment_option,
            payment_method=order.payment_method,
            coupon=order.coupon,
            shipping_address=order.shipping_address,
            billing_address=order.billing_address,
        )
        new_one.save()
        for item in order.items.all():
            new_item = item
            new_item.pk = None
            new_item.order = new_one
            new_item.save()

    except Exception as e:
        print("Exception order_reorder", e)
        messages.error(req, "Référence de commande non valide")
    return redirect("checkout")


@login_required
def order_modify(req, ref):
    try:
        order = Order.objects.get(ref_code=ref)
    except Exception as e:
        print("exception order_modify", e)
        messages.error(req, "Référence de commande non valide ")
        return redirect("user-orders")
    if not order.order_status == "ON HOLD":
        messages.error(req, "Can't modify this order ")
        return redirect("user-orders")
    if req.method == "POST":
        if req.POST.get('action') == "deletemessage":
            order.message = None
            order.save()
            messages.success(req, "Message deleted")
            redirect("order-modify", ref=order.ref_code)
        if req.POST.get('action') == "deletecoupon":
            order.coupon = None
            order.save()
            messages.success(req, "Coupon deleted")
            redirect("order-modify", ref=order.ref_code)
        if req.POST.get('action') == "changeaddress":
            try:
                addresse = Address.objects.get(id=req.POST.get('address_id'))
                order.shipping_address = addresse
                order.save()
                messages.success(req, "Address Updated")
            except Exception as e:
                print("Exception order_modify", e)
                messages.error(req, "Non valid address")
        coupon = CouponForm(req.POST or None)
        message = MessageForm(req.POST or None)
        if coupon.is_valid():
            if coupon.cleaned_data.get('code'):
                if order.coupon:
                    if order.coupon.code == coupon.cleaned_data['code']:
                        messages.warning(req, "You already added this coupon ")
                else:
                    try:
                        coupon = Coupon.objects.get(code=coupon.cleaned_data['code'], expire_date__gte=timezone.now())
                        if order:
                            order.coupon = coupon
                            order.save()
                            messages.success(req, "Coupon added successfully ")
                        else:
                            messages.warning(req, "Vous n'avez pas de commande active ")
                    except Exception as e:
                        print("Exception order_modify", e)
                        messages.warning(req, "Le coupon n'est pas valide ou a expiré !")

            else:
                messages.warning(req, "Coupon non valide !")
        elif message.is_valid():
            if message.cleaned_data.get('message'):
                try:
                    order.message = message.cleaned_data["message"]
                    order.save()
                except Exception as e:
                    print("Exception order_modify", e)
                    messages.error(req, "Erreur lors de l'obtention de votre commande")
                messages.success(req, "Instructions added")
        elif not message.is_valid():
            messages.warning(req, "Erreur lors de la réception du message")
        else:
            messages.warning(req, "Erreur lors de la réception du coupon")
    context = {
        "modify": True,
        "order": order,
        "coupon": CouponForm(),
        "message": MessageForm(initial={"message": order.message})
    }
    return render(req, "customer-order.html", context)


@login_required
def profile(req):
    form = ChangePasswordForm()
    user = req.user
    # user_profile = user.user_profile.all()[0]
    user_profile = user.user_profile
    if user_profile:
        data = {'gender': user_profile.gender, 'firstname': user.first_name, 'lastname': user.last_name,
                'telephone': user_profile.telephone,
                'email': user.email}
    else:
        data = {}
    if req.method == 'POST':
        if req.POST.get("picture"):
            image = ImageForm(req.POST, req.FILES)
            if image.is_valid():
                image = image.save()
                if user_profile:
                    user_profile.profile_picture = image
                    user_profile.save()
                else:
                    user_profile = UserProfile()
                    user_profile.user = user
                    user_profile.profile_picture = image
                    user_profile.save()
                messages.success(req, "Image uploaded successfully")
                image = ImageForm()
            else:
                messages.error(req, image.errors)

            userprofile = UserProfileForm(initial=data)
        elif req.POST.get("infos"):
            userprofile = UserProfileForm(req.POST)
            if userprofile.is_valid():
                user.first_name = userprofile.cleaned_data['firstname']
                user.last_name = userprofile.cleaned_data['lastname']
                user.email = userprofile.cleaned_data['email']
                user.save()
                if user_profile:
                    user_profile.gender = userprofile.cleaned_data['gender']
                    user_profile.telephone = userprofile.cleaned_data['telephone']
                    user_profile.save()
                else:
                    user_profile = UserProfile()
                    user_profile.user = user
                    user_profile.gender = userprofile.cleaned_data['gender']
                    user_profile.telephone = userprofile.cleaned_data['telephone']
                    user_profile.save()
                messages.success(req, "Personal information uploaded successfully")
            else:
                messages.error(req, "Error in form")

            image = ImageForm()
    else:
        userprofile = UserProfileForm(initial=data)
        image = ImageForm()

    context = {
        "form": form,
        "userprofile": userprofile,
        "image": image,
    }
    return render(req, "customer-account.html", context)


@login_required
def addresses(req):
    modify = None
    form = AddressForm()
    id = req.POST.get('id', None)
    if req.method == "POST":
        action = req.POST.get('action')
        if action == "add":
            form = AddressForm(req.POST or None)
            if form.is_valid():
                address = Address(**form.cleaned_data)
                address.user = req.user
                address.save()
                messages.success(req, "Address Saved")
                form = AddressForm()
            else:
                messages.error(req, "Errors in Form")
        else:
            if id:
                try:
                    address = Address.objects.get(id=id)
                except Exception as e:
                    print("exception addresses", e)
                    messages.error(req, "Non valid Address")
                    return redirect("user-addresses")
                if action == "updated":
                    form = AddressForm(req.POST or None)
                    if form.is_valid():
                        Address.objects.filter(id=id).update(**form.cleaned_data)
                        messages.info(req, "Address Updated")
                        form = AddressForm()
                    else:
                        modify = True
                        messages.error(req, "Errors in Form")

                if action == "Modify":
                    form = AddressForm(initial=model_to_dict(address))
                    modify = True
                elif action == "Delete":
                    address.delete()
                    messages.info(req, "Address Deleted")
                elif action == "Default":
                    try:
                        def_address = req.user.addresses.filter(default=True)[0]
                        def_address.default = False
                        def_address.save()
                    except Exception as e:
                        print("exception addresses", e)
                        pass
                    address.default = True
                    address.save()
                    messages.info(req, "Address is set to default")
            else:
                messages.error(req, "Non valid Address")
    context = {
        "form": form,
        "modify": modify,
        "id": id,
        "user_addresses": req.user.addresses.all
    }
    return render(req, "customer-addresses.html", context)


@login_required
def checkout(req):
    try:
        order = Order.objects.filter(user=req.user, ordered=False)[0]
    except Exception as e:
        print("exception checkout 1", e)
        messages.error(req, "Non Valid order")
        return redirect("home")
    form = AddressForm()
    if req.method == "POST":
        if req.POST.get('action') == "choseanaddress":
            try:
                addresse = Address.objects.get(id=req.POST.get('address_id'))
            except Exception as e:
                print("exception checkout 2", e)
                messages.error(req, "Non valid address")
            order.shipping_address = addresse
            order.save()
            messages.success(req, "Address Added")
            return redirect("delivery")
        else:
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
    except Exception as e:
        print("exception delivery", e)
        messages.error(req, "Non Valid order")
        return redirect("home")
    if req.method == "POST":
        try:
            method = DeliveryMethod.objects.get(id=req.POST.get('option_id', None))
            order.delivery_method = method
            order.save()
            return redirect("payment")
        except Exception as e:
            print("exception delivery", e)
            messages.error(req, "Non Valid Method")

    user_method = order.delivery_method
    if user_method:
        methods = DeliveryMethod.objects.exclude(id=user_method.id)
    else:
        methods = DeliveryMethod.objects.all()

    context = {
        "methods": methods,
        "user_method": user_method,
    }
    return render(req, "checkout2.html", context)


@login_required
def update_delivery(req, ref):
    try:
        order = Order.objects.get(ref_code=ref)
    except Exception as e:
        print("exception update_delivery", e)
        messages.error(req, "Non Valid order")
        return redirect("home")
    if req.method == "POST":
        try:
            method = DeliveryMethod.objects.get(id=req.POST.get('option_id', None))
            print("method", method)
            order.delivery_method = method
            order.save()
            print("all ", method.payment_options.all())
            print("current ", order.payment_option)
            if order.payment_option not in method.payment_options.all():
                order.payment_option = None
                order.payment_method = None
                order.save()
                return redirect("update-payment", ref=ref)
            return redirect("order-modify", ref=ref)
        except Exception as e:
            print("Exception update_delivery", e)
            messages.error(req, "Non Valid Method")
    else:
        redirect("user-orders")

    user_method = order.delivery_method
    if user_method:
        methods = DeliveryMethod.objects.exclude(id=user_method.id)
    else:
        methods = DeliveryMethod.objects.all()

    context = {
        "methods": methods,
        "user_method": user_method,
        "change": True
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
    except Exception as e:
        print("exception payment", e)
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
            except Exception as e:
                print("exception payment", e)
                messages.error(req, "Non Valid option")
        elif req.POST.get('e2option_id'):
            try:
                payment_method = PaymentMethod.objects.get(id=req.POST['e2option_id'])
                order.payment_method = payment_method
                order.save()
                return redirect("overview")
            except Exception as e:
                print("exception payment", e)
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
def update_payment(req, ref):
    payment_methods = None
    try:
        order = Order.objects.get(ref_code=ref)
    except Exception as e:
        print("exception update_payment", e)
        messages.error(req, "Non Valid order")
        return redirect("home")

    if req.method == "POST":
        if req.POST.get('option_id'):
            try:
                payment_option = PaymentOptions.objects.get(id=req.POST['option_id'])
                order.payment_option = payment_option
                order.save()
                payment_methods = payment_option.payment_methods.all()
                return render(req, "checkout3.html", {"payment_methods": payment_methods, "change": True})
            except Exception as e:
                print("exception update_payment", e)
                messages.error(req, "Non Valid option")
        elif req.POST.get('e2option_id'):
            try:
                payment_method = PaymentMethod.objects.get(id=req.POST['e2option_id'])
                order.payment_method = payment_method
                order.save()
                return redirect("order-modify", ref=ref)
            except Exception as e:
                print("exception update_payment", e)
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
        "change": True
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
    except Exception as e:
        print("exception overview", e)
        messages.error(req, "The card is empty !")
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
    except Exception as e:
        print("exception confirmation", e)
        messages.error(req, "Non Valid order !")
        return redirect("home")
    try:
        order.ordered = True
        order.ordered_date = timezone.now()
        order.order_status = "ON HOLD"
        order.save()
        try:
            email = order.user.email
            if order.payment_method.name == "Virement bancaire":
                context = {
                    "price": order.get_total(),
                    'name': order.user.get_full_name(),
                    "ref": order.ref_code
                }
                html = get_template('dashboard/order_confirmation_email.html')
                objet = f"COMMANDE {order.ref_code} - EN ATTENTE DU PAIEMENT"
            else:
                context = {
                    "price": order.get_total(),
                    'name': order.user.get_full_name(),
                    "ref": order.ref_code
                }
                html = get_template('dashboard/order_confirmation_email_phone.html')
                objet = f"COMMANDE {order.ref_code} - EN ATTENTE DE VALIDATION PAR TÉLÉPHONE"
            html_content = html.render(context)
            text_content = strip_tags(html_content)
            msg = EmailMultiAlternatives(objet, text_content,
                                         settings.EMAIL_HOST,
                                         [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
        except Exception as e:
            print("Couldn't send the mail ", e)
    except Exception as e:
        print("exception confirmation", e)
        messages.error(req, "Error while saving your order")
        return redirect("overview")
    context = {
        "user": req.user,
    }
    return render(req, "checkout5.html", context)


def send_welcome_mail(email, red):
    try:
        newsletter_obj = NewsLetter.objects.get(title='Bienvenue chez FoxProds')
        text_content = strip_tags(newsletter_obj.content)
        msg = EmailMultiAlternatives(newsletter_obj.title, text_content, settings.EMAIL_HOST, [email])
        msg.attach_alternative(newsletter_obj.content, "text/html")
        msg.send()
    except Exception as ex:
        print("Exception send_welcome_mail", ex)
        return redirect(red)


def newsletter(req):
    if req.POST:
        form = NewsLetterEmailForm(req.POST or None)
        if form.is_valid():
            email_form = form.save(commit=False)
            try:
                NewsLetterEmail.objects.get(email=email_form.email)
                messages.warning(req, "votre email existe déjà dans notre base de données")
            except Exception as e:
                print("Exception newsletter", e)
                email_form.save()
                try:
                    send_welcome_mail(email_form.email, req.POST.get("next", 'home'))
                except Exception as e:
                    print("Exception newsletter", e)
                    pass
                messages.success(req, "Email ajouter avec succès ")
        else:
            messages.error(req, form.errors)
    return redirect(req.POST.get("next", 'home'))
