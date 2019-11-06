from calendar import monthrange
from datetime import timedelta, datetime

from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import make_aware

from core.forms import *
from dashboard.forms import *
from .utils import render_to_pdf, HttpResponse


def demo(req):
    try:
        email = "vala.stage.3@gmail.com"
        html = get_template('dashboard/welcome_mail.html')
        html_content = html.render({'email': email})
        text_content = strip_tags(html_content)
        msg = EmailMultiAlternatives("Bienvenue chez FoxProds", text_content, settings.EMAIL_HOST,
                                     [email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()
    except Exception as ex:
        print("Exception ", ex)
        return HttpResponse("Exception ", ex)

    return HttpResponse("Done")


def generate_pdf(req, ref):
    try:
        order = Order.objects.get(ref_code=ref)
        pdf = render_to_pdf('dashboard/demo.html', {'order': order})
    except:
        messages.error(req, "Référence non valide")
        return redirect("user-orders")
    return HttpResponse(pdf, content_type='application/pdf')


def get_sales_values():
    year = datetime.now().year
    month = datetime.now().month
    months = [x for x in range(1, 12) if x <= month]
    result = []
    for month in months:
        total = 0
        beg = make_aware(datetime(year, month, 1, 0, 0, 0, 0))
        end = make_aware(datetime(year, month, monthrange(year, month)[1], 23, 59, 59, 999999))
        orders = Order.objects.filter(complete_date__gte=beg, complete_date__lte=end)
        for order in orders:
            print(order.get_total_coupon)
            total += order.get_total_coupon
        result.append(total)
    print(result)
    return result


@staff_member_required
def dashboard(req):
    this_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = this_month - timedelta(days=30)
    last_month_end = timezone.now() - timedelta(days=30)

    nbr_requests = Order.objects.filter(order_status="ON HOLD").count()
    nbr_messages = Contact.objects.filter(seen=False).count()
    new_clients = User.objects.filter(date_joined__gt=this_month).count()
    new_clients_last = User.objects.filter(date_joined__gt=last_month_start, date_joined__lt=last_month_end).count()

    try:
        percent_client = ((new_clients - new_clients_last) / new_clients_last) * 100
    except ZeroDivisionError:
        percent_client = new_clients * 100

    new_sales = Order.objects.filter(order_status="COMPLETED", complete_date__gt=this_month).count()
    last_sales = Order.objects.filter(order_status="COMPLETED", complete_date__gt=last_month_start,
                                      complete_date__lt=last_month_end).count()
    try:
        percent_sales = ((new_sales - last_sales) / last_sales) * 100
    except ZeroDivisionError:
        percent_sales = new_sales * 100

    context = {
        "nbr_requests": nbr_requests,
        "nbr_messages": nbr_messages,
        "new_clients": new_clients,
        "percent_client": percent_client,
        "new_sales": new_sales,
        "percent_sales": percent_sales,
        "sales_values": get_sales_values()
    }
    return render(req, "dashboard/index.html", context)


@staff_member_required
def commandes(req):
    if req.POST:
        if req.POST.get("search"):
            return redirect("db:order-details", ref=req.POST.get("ref"))
        ref = req.POST.get("ref" or None)
        choice = req.POST.get("choice" or None)
        try:
            order = Order.objects.get(ref_code=ref)
            result = [k for (k, v) in Order._meta.get_field('order_status').choices if choice == v]
            order.order_status = result[0]
            if order.order_status == "COMPLETED":
                order.complete_date = timezone.now()
            order.save()
        except Exception as e:
            print(e)
            messages.error(req, "Une erreur est survenue")
    orders = Order.objects.filter(ordered=True)
    context = {
        "orders": orders,
        "choices": [v for (k, v) in Order._meta.get_field('order_status').choices]
    }
    return render(req, "dashboard/commandes.html", context)


@staff_member_required
def db_order_details(req, ref):
    print("ref ", ref)
    step2 = None
    try:
        order = Order.objects.get(ref_code=ref)
    except Exception as e:
        print("exception ", e)
        messages.error(req, "Code de référence non valide ")
        return redirect("db:commandes")
    if req.method == "POST":
        if req.POST.get('action') == "changemethod":
            try:
                order.payment_method = PaymentMethod.objects.get(id=req.POST.get('pmethod_id'))
                order.save()
                messages.success(req, "Mise à jour réussie")
            except Exception as e:
                print(e)
                messages.success(req, "Mode non valide")
            redirect("order-modify", ref=order.ref_code)
        if req.POST.get('action') == "changemodedb":
            try:
                mode = DeliveryMethod.objects.get(id=req.POST.get('mode_id'))
                order.delivery_method = mode
                order.payment_option = None
                order.payment_method = None
                order.save()
                messages.success(req, "Mise à jour réussie")
            except Exception as e:
                print(e)
                messages.success(req, "Mode non valide")
            redirect("order-modify", ref=order.ref_code)
        elif req.POST.get('action') == "deletemessage":
            order.message = None
            order.save()
            messages.success(req, "Message deleted")
            redirect("order-modify", ref=order.ref_code)
        elif req.POST.get('action') == "deletecoupon":
            order.coupon = None
            order.save()
            messages.success(req, "Coupon deleted")
            redirect("order-modify", ref=order.ref_code)
        elif req.POST.get('action') == "changeaddress":
            try:
                addresse = Address.objects.get(id=req.POST.get('address_id'))
                order.shipping_address = addresse
                order.save()
                messages.success(req, "Address Updated")
            except Exception as e:
                print("exception", e)
                messages.error(req, "Non valid address")
        elif req.POST.get('action') == "changemodalitedb":
            try:
                modalite = PaymentOptions.objects.get(id=req.POST.get('modalite_id'))
                order.payment_option = modalite
                order.payment_method = None
                order.save()
                messages.success(req, "Mise à jour réussie")
            except Exception as e:
                print(e)
                messages.success(req, "Error")
            step2 = True
            redirect("order-modify", ref=order.ref_code)
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
                            messages.warning(req, "You do not have an active order ")
                    except Exception as e:
                        print("exception", e)
                        messages.warning(req, "Coupon is None Valid or expired !")

            else:
                messages.warning(req, "Non Valid Coupon !")
        elif message.is_valid():
            if message.cleaned_data.get('message'):
                try:
                    order.message = message.cleaned_data["message"]
                    order.save()
                except Exception as e:
                    print("exception", e)
                    messages.error(req, "Error getting your order")
                messages.success(req, "Instructions added")
        elif not message.is_valid():
            messages.warning(req, "Error getting the Message")
        else:
            messages.warning(req, "Error getting the Coupon")

    payment_options = order.delivery_method.payment_options if order.delivery_method else None
    payment_methods = order.payment_option.payment_methods if step2 else None
    context = {
        "order": order,
        "methods": DeliveryMethod.objects.all(),
        "modify": True,  # if order.order_status == "ON HOLD" else False,
        "coupon": CouponForm(),
        "message": MessageForm(initial={"message": order.message}),
        "payment_options": payment_options,
        "payment_methods": payment_methods,
    }
    return render(req, "dashboard/order-details.html", context)


@staff_member_required
def products(req):
    if req.POST:
        try:
            product = Product.objects.get(slug=req.POST.get("ref" or None))
            if req.POST.get("visible"):
                product.visible = req.POST.get("visible")
                product.save()
            elif req.POST.get("featured"):
                product.is_featured = req.POST.get("featured")
                product.save()
        except:
            messages.error(req, "Une erreur est survenue")
            redirect("db:products")

    products = Product.objects.all()
    categories = Category.objects.all()
    context = {
        "products": products,
        "categories": categories,
    }
    return render(req, "dashboard/products.html", context)


@staff_member_required
def db_delete_product(req, ref):
    try:
        product = Product.objects.get(slug=ref)
        product.delete()
    except Exception as e:
        messages.error(req, "Ref ou Product non valable")
        print("Exception", e)
    messages.success(req, "Produit supprimé")
    return redirect("db:products")


@staff_member_required
def db_add_product(req):
    image = ImageForm()
    if req.POST:
        form = ProductForm(req.POST or None)
        if form.is_valid():
            try:
                product = form.save(commit=False)
                product.slug = slugify(form.cleaned_data["product_name"])
                product.save()
                product.product_categorie.set(form.cleaned_data["product_categorie"])
                product.related_products.set(form.cleaned_data["related_products"])
                product.product_attributes.set(form.cleaned_data["product_attributes"])
                # product.product_attributes.set(req.POST.get("attributes"))
                product.tags.set(form.cleaned_data["tags"])

                for i, file in enumerate(req.FILES.getlist('images')):
                    print("index", i)
                    image = Image(
                        is_primary=True if not i else False,
                        alt=f"{product.slug} {i + 1}",
                        image=file
                    )
                    image.save()
                    product.product_images.add(image)
                product.save()
                messages.success(req, "Produit ajouté")
            except Exception as e:
                messages.error(req, e)
                print("Exception :", e)
        else:
            messages.error(req, "Errors dans la form")

    context = {
        "product_form": ProductForm(),
        "image": image,
    }
    return render(req, "dashboard/add_product.html", context)


@staff_member_required
def db_product_details(req, ref):
    try:
        product = Product.objects.get(slug=ref)
        print(product.product_images.all())
    except Exception as e:
        product = None
        print(e)
        messages.error(req, "Une erreur est survenue")
        redirect("db:products")
    context = {
        "product": product,
        "product_form": ProductForm(instance=product),
    }
    return render(req, "dashboard/product-details.html", context)


@staff_member_required
def categories(req):
    return None


@staff_member_required
def db_category_details(req):
    return None


@staff_member_required
def db_add_category(req):
    if req.POST:
        category_form = CategoryForm(req.POST)
        image_form = ImageForm(req.POST, req.FILES)
        if category_form.is_valid() and image_form.is_valid():
            try:
                category = category_form.save(commit=False)
                category.slug = slugify(category.name)

                image = image_form.save(commit=False)
                image.is_primary = True
                image.alt = category.name
                image.save()

                category.image = image
                category.save()
                messages.success(req, "Catégorie ajoute")
            except Exception as e:
                messages.error(req, "Error " + str(e))
                print("Exception", e)
    category_form = CategoryForm()
    image_form = ImageForm()
    context = {
        "category_form": category_form,
        "image_form": image_form,
    }
    return render(req, "dashboard/add_category.html", context)


@staff_member_required
def attributes(req):
    return None


@staff_member_required
def db_attribute_details(req):
    return None


@staff_member_required
def db_add_attribute(req):
    if req.POST:
        print(req.POST)
        attributes_form = AttributesForm(req.POST)
        option_form = OptionForm(req.POST)
        option_values_form = OptionsValuesForm(req.POST)
        if attributes_form.is_valid():
            try:
                attributes_form.save()
                messages.success(req, "Attribute ajoute")
            except:
                messages.success(req, "Error")
        elif option_form.is_valid():
            try:
                option_form.save()
                messages.success(req, "Option ajoute")
            except:
                messages.success(req, "Error")
        elif option_values_form.is_valid():
            try:
                option_values_form.save()
                messages.success(req, "Valeur ajoute")
            except:
                messages.success(req, "Error")

    attributes_form = AttributesForm()
    option_form = OptionForm()
    option_values_form = OptionsValuesForm()
    context = {
        "attributes_form": attributes_form,
        "option_form": option_form,
        "option_values_form": option_values_form,
    }
    return render(req, "dashboard/add_attribute.html", context)


@staff_member_required
def users(req):
    if req.POST:
        try:
            user = User.objects.get(username=req.POST.get("ref" or None))
            if req.POST.get("is_active"):
                user.is_active = req.POST.get("is_active")
                user.save()
            elif req.POST.get("is_superuser"):
                user.is_superuser = req.POST.get("is_superuser")
                user.save()
        except Exception as e:
            messages.error(req, "Une erreur est survenue")
            print("Exception", e)

    users = User.objects.all().order_by("-date_joined")
    context = {
        "users": users,
    }
    return render(req, "dashboard/users.html", context)


def save_user(user_form, profile_form, address_form, image_form):
    user = user_form.save()
    image = image_form.save(commit=False)
    image.alt = f"Photo de profile de {user.first_name} {user.last_name}"
    image.is_primary = True
    image.save()
    profile = profile_form.save(commit=False)
    address = address_form.save(commit=False)
    address.user = user
    address.full_name = f"{user.first_name} {user.last_name}"
    address.phone_number = profile.telephone
    address.default = True
    address.save()
    profile = profile_form.save(commit=False)
    profile.user = user
    profile.profile_picture = image
    profile.address = address
    profile.save()


@staff_member_required
def db_user_details(req, ref):
    success = False
    user = get_object_or_404(User, username=ref)
    user_form = UserForm(instance=user)
    image_form = ImageForm(instance=user.user_profile.profile_picture)
    profile_form = ProfileForm(instance=user.user_profile)
    address_form = AddressForm(instance=user.user_profile.address)
    if req.POST:
        address_post = req.POST.copy()
        address_post['full_name'] = 'z'
        address_post['phone_number'] = '0652124680'

        user = User.objects.get(username=req.POST.get('username'))
        user_form = UserForm(req.POST, instance=user)
        profile_form = ProfileForm(req.POST, instance=user.user_profile)
        address_form = AddressForm(address_post, instance=user.user_profile.address)
        image_form = ImageForm(req.POST, req.FILES, instance=user.user_profile.profile_picture)
        if profile_form.is_valid() and user_form.is_valid() and image_form.is_valid() and address_form.is_valid():
            try:
                save_user(user_form, profile_form, address_form, image_form)
                messages.success(req, "Utilisateur modifié")
                success = True
            except Exception as e:
                print("Exception", e)
                messages.error(req, "Error ")
        else:
            messages.error(req, "Form non valide ")
    context = {
        "modify": 1,
        "user_form": user_form,
        "profile_form": profile_form,
        "image_form": image_form,
        "address_form": address_form,
        "md_succes": success,
    }
    return render(req, "dashboard/add_user.html", context)


@staff_member_required
def db_add_user(req, ):
    success = False
    user_form = UserForm()
    image_form = ImageForm()
    profile_form = ProfileForm()
    address_form = AddressForm()
    if req.POST:
        address_post = req.POST.copy()
        address_post['full_name'] = 'z'
        address_post['phone_number'] = '0652124680'
        user_form = UserForm(req.POST)
        profile_form = ProfileForm(req.POST)
        address_form = AddressForm(address_post)
        image_form = ImageForm(req.POST, req.FILES)

        if profile_form.is_valid() and user_form.is_valid() and image_form.is_valid() and address_form.is_valid():
            try:
                save_user(user_form, profile_form, address_form, image_form)
                messages.success(req, "Utilisateur ajoute")
                success = True
            except Exception as e:
                print("Exception", e)
                messages.error(req, "Error ")
        else:
            messages.error(req, "Form non valide ")
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "image_form": image_form,
        "address_form": address_form,
        "success": success,
    }
    return render(req, "dashboard/add_user.html", context)


@staff_member_required
def db_delete_user(req, ref):
    try:
        user = User.objects.get(slug=ref)
        user.delete()
    except Exception as e:
        messages.error(req, "Ref ou Utilisateur non valable")
        print("Exception", e)
    messages.success(req, "Utilisateur supprimé")
    return redirect("db:users")


@staff_member_required
def analytique(req):
    pass


@staff_member_required
def contacts(req):
    msgs = Contact.objects.all()
    context = {
        "messages": msgs,
    }
    return render(req, "dashboard/messages.html", context)


@staff_member_required
def db_messages_details(req, ref):
    try:
        message = Contact.objects.get(id=ref)
        message.seen = True
        message.save()
    except Exception as e:
        message = None
        print(e)
        messages.error(req, "Une erreur est survenue")
        redirect("db:messages")
    context = {
        "message": message,
    }
    return render(req, "dashboard/message-details.html", context)


@staff_member_required
def db_delete_message(req, ref):
    try:
        msg = Contact.objects.get(id=ref)
        msg.delete()
    except Exception as e:
        messages.error(req, "ID ou Message non valable")
        print("Exception", e)
    messages.success(req, "Message supprimé")
    return redirect("db:messages")


@staff_member_required
def newsletter(req):
    newsletters = NewsLetter.objects.all().order_by('-date_added')
    context = {
        "newsletters": newsletters,
    }
    return render(req, "dashboard/newsletter.html", context)


@staff_member_required
def add_newsletter(req):
    newsletter_form = NewsLetterForm(req.POST or None)
    if req.POST:
        if newsletter_form.is_valid():
            newsletter_form.save()
            messages.success(req, 'Newsletter ajouté')
        else:
            messages.error(req, 'Error')
    context = {
        "newsletter_form": newsletter_form,
    }
    return render(req, "dashboard/add_newsletter.html", context)


@staff_member_required
def newsletter_details(req, ref):
    try:
        newsletter = NewsLetter.objects.get(id=ref)
    except:
        return redirect("db:newsletter")
    newsletter_form = NewsLetterForm(req.POST or None, instance=newsletter)
    if req.POST:
        if newsletter_form.is_valid():
            newsletter_form.save()
            messages.success(req, 'Newsletter modifié avec succès')
        else:
            messages.error(req, 'Error')
    context = {
        "newsletter_form": newsletter_form,
        "modify": True
    }
    return render(req, "dashboard/add_newsletter.html", context)


@staff_member_required
def send_newsletter(req, ref):
    try:
        emails = NewsLetterEmail.objects.filter(is_active=True).values_list('email', flat=True)
        newsletter_obj = NewsLetter.objects.get(id=ref)
        text_content = strip_tags(newsletter_obj.content)
        msg = EmailMultiAlternatives(newsletter_obj.title, text_content, settings.EMAIL_HOST, bcc=emails)
        msg.attach_alternative(newsletter_obj.content, "text/html")
        msg.send()
    except Exception as exc:
        print("Exception", exc)
        messages.error(req, "Error")
    messages.success(req, "Newsletter envoyé")
    return redirect("db:newsletter")


@staff_member_required
def del_newsletter(req, ref):
    try:
        NewsLetter.objects.get(id=ref).delete()
    except Exception as exc:
        print("Exception", exc)
        messages.error(req, "Error")
    messages.success(req, "Newsletter supprimé")
    return redirect("db:newsletter")


@staff_member_required
def newsletter_emails(req):
    if req.POST:
        try:
            newsletter = NewsLetterEmail.objects.get(id=req.POST.get("ref" or None))
            if req.POST.get("active"):
                newsletter.is_active = req.POST.get("active")
                newsletter.save()
        except:
            messages.error(req, "Une erreur est survenue")
            redirect("db:newsletter-emails")
    newsletters_emails = NewsLetterEmail.objects.all().order_by('-date_added')
    context = {
        "newsletters_emails": newsletters_emails,
    }
    return render(req, "dashboard/newsletter_emails.html", context)


@staff_member_required
def del_newsletter_email(req, ref):
    try:
        NewsLetterEmail.objects.get(id=ref).delete()
    except Exception as exc:
        print("Exception", exc)
        messages.error(req, "Error")
    messages.success(req, "Email supprimé")
    return redirect("db:newsletter-emails")
