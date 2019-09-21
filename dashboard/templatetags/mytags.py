from django import template

from core.forms import NewsLetterForm
from core.models import Category, Order, Address

register = template.Library()


@register.filter
def sub(value, arg):
    return value - arg


@register.inclusion_tag("navbar_categories.html")
def show_all_categories():
    nav_categories = Category.objects.filter(parent_category__isnull=True)
    return {
        'categories': nav_categories,
    }


def get_order(req):
    order = None
    if req.user.is_authenticated:
        order_qs = Order.objects.filter(user=req.user, ordered=False)
        if order_qs.exists():
            order = order_qs[0]
    else:
        try:
            order_id = req.session['cart']
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                # messages.error(req,"This order is deleted or not available")
                pass
        except KeyError:
            pass
    return order


def get_order_count(req):
    try:
        return get_order(req).items.count(), False
    except:
        return 0, True


@register.simple_tag(takes_context=True)
def profile_order_count(context):
    return Order.objects.filter(user=context['request'].user, ordered=True).count()


@register.simple_tag
def newsletter_form():
    return NewsLetterForm()


@register.simple_tag(takes_context=True)
def cart_count(context):
    return get_order_count(context['request'])[0]


@register.inclusion_tag("profile-sidebar.html", takes_context=True)
def show_profile_sidebar(context):
    user = context['request'].user
    count = Order.objects.filter(user=context['request'].user, ordered=True).count()
    addresse = Address.objects.filter(user=user, default=True)
    if addresse.exists():
        addresse = f"{addresse[0].city} , {addresse[0].country} "
    return {
        'user': user,
        'count': count,
        "addresse": addresse,
        "path": context['request'].path.strip('/')
    }


@register.inclusion_tag("cart_products.html", takes_context=True)
def show_cart_products(context):
    req = context['request']
    count, display = get_order_count(req)
    return {
        'order': get_order(req),
        'count': count,
        'display': display

    }


@register.inclusion_tag("order_summary.html", takes_context=True)
def order_summary(context):
    req = context['request']
    return {
        'order': get_order(req),
    }
