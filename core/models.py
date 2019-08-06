from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.shortcuts import reverse

# Create your models here.
TAG_CHOICES = [
    ('PRIMARY', 'primary'),
    ('SECONDARY', 'secondary'),
    ('SUCCESS', 'success'),
    ('DANGER', 'danger'),
    ('WARNING', 'warning'),
    ('INFO', 'info'),
]
STATUS_CHOICES = [
    ('ON HOLD', 'On Hold'),
    ('PROCESSING', 'Processing'),
    ('CANCELED', 'Canceled'),
    ('FAILED', 'Failed'),
    ('COMPLETED', 'Completed'),
    ('REFUNDED', 'Refunded')
]
GENDER_CHOICES = [
    ('F', 'Female'),
    ('M', 'Male'),
]


class BaseModel(models.Model):
    date_added = models.DateTimeField(auto_now_add=True, editable=False)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Image(BaseModel):
    image = models.ImageField()
    alt = models.CharField(max_length=200)
    is_primary = models.BooleanField(default=False)

    class Meta:
        db_table = "Image"

    def __str__(self):
        return self.alt

    def get_absolute_url(self):
        return self.image.url


class Category(BaseModel):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    parent_category = models.ForeignKey(
        'self', on_delete=models.SET_NULL, related_name='child_categories', null=True, blank=True)
    image = models.ImageField(blank=True, null=True)
    tags = models.ManyToManyField("Tag", related_name='categories', blank=True)

    class Meta:
        db_table = "Category"
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        # if not self.parent_category :
        #     return reverse("shop")
        return reverse("shop_by_category", kwargs={"slug": self.slug})

    def get_featured_products(self):
        return self.products.all().filter(visible=True)

    def get_parent_products(self):
        if self.parent_category:
            return None
        else:
            products = []
            for category in self.child_categories.all():
                for product in category.products.all():
                    products.append(product)
        return products


class Banner(BaseModel):
    title = models.CharField(max_length=250)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=False)
    image = models.ImageField()
    show_date = models.DateTimeField(auto_now_add=True)
    expire_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "Banner"

    def __str__(self):
        return self.title


class BannerHistory(BaseModel):
    banner = models.OneToOneField(Banner, on_delete=models.CASCADE)
    banner_shown = models.PositiveIntegerField(default=0)
    banner_clicked = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "banner_history"


class Product(BaseModel):
    product_name = models.CharField(max_length=100)
    product_into = models.CharField(max_length=200, default="")
    # TODO: Convert it to HTMLField
    product_description = models.TextField()
    slug = models.SlugField(unique=True)

    product_viewed = models.IntegerField(default=0)
    product_quantity_available = models.IntegerField(default=10)

    product_price = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    product_price_onsale = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True, validators=[MinValueValidator(0)])

    visible = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)

    product_date_available = models.DateTimeField(blank=True, null=True)

    product_images = models.ManyToManyField(Image)

    product_categorie = models.ManyToManyField(
        Category, related_name='products')

    related_products = models.ManyToManyField(
        'self', related_name='related_products', blank=True)

    product_attributes = models.ManyToManyField(
        'Product_attributes', related_name='products')

    additional_options = models.ManyToManyField(
        'Product_Options', related_name='products', blank=True)

    tags = models.ManyToManyField("Tag", blank=True, related_name='products')

    class Meta:
        db_table = "Product"

    def __str__(self):
        return f"{self.product_quantity_available} of {self.product_name}"

    def get_price(self):
        return self.product_price_onsale if self.product_price_onsale else self.product_price

    def get_absolute_url(self):
        return reverse("product-details", kwargs={"slug": self.slug})

    def get_add_to_cart_url(self):
        return reverse("add-to-cart", kwargs={
            'slug': self.slug
        })

    def get_add_to_favorites_url(self):
        return reverse("add-to-cart", kwargs={
            'slug': self.slug
        })

    def remove_form_cart(self):
        return reverse("product-details", kwargs={"slug": self.slug})

    def get_primary_image(self):
        for image in self.product_images.all():
            if image.is_primary:
                return image
        return self.product_images.all()[0]


class Product_Options(BaseModel):
    option_name = models.CharField("option name", max_length=200)
    category = models.ManyToManyField(Category)

    option_values = models.ManyToManyField(
        "Product_Options_Values", related_name='options')

    class Meta:
        db_table = "Product_Options"
        verbose_name_plural = 'Product options'

    def __str__(self):
        return self.option_name


class Product_Options_Values(BaseModel):
    value = models.CharField("option name", max_length=200)
    price = models.DecimalField(
        "Price of an option", max_digits=10, decimal_places=2, default=0, null=True)

    class Meta:
        db_table = "Product_Options_Values"
        verbose_name_plural = 'Product option values'

    def __str__(self):
        return f"{self.value} | + {self.price} DH"


class Product_attributes(BaseModel):
    option = models.ForeignKey(
        Product_Options, related_name='Product_attributes', on_delete=models.CASCADE)
    option_value = models.ForeignKey(
        Product_Options_Values, related_name='Product_attributes', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = "Product_attributes"
        verbose_name_plural = 'Product attributes'

    def __str__(self):
        return f"{self.option.option_name} - {self.option_value.value} "


class Tag(BaseModel):
    tag = models.CharField(max_length=50)
    type = models.CharField(
        max_length=10,
        choices=TAG_CHOICES,
        blank=True, null=True
    )

    def __str__(self):
        return f"{self.tag} - {self.type}"

    class Meta:
        db_table = "Tags"


class OrderItem(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(
        "Order", related_name="items", on_delete=models.CASCADE)
    additional_options = models.ManyToManyField(
        Product_Options_Values, blank=True)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.product.product_name}"

    def get_additional_options_price(self):
        sum = 0
        for option in self.additional_options.all():
            sum = int(option.price)
        return sum

    def get_total_price(self):
        return ((
                    self.product.product_price_onsale if self.product.product_price_onsale else self.product.product_price) + self.get_additional_options_price())

    def get_subtotal(self):
        return self.quantity * self.get_total_price()

    def remove_form_cart(self):
        return reverse("remove_form_cart", kwargs={"id": self.id})

    def increment_item_card(self):
        return reverse("increment_item_card", kwargs={"id": self.id})

    def decrement_item_card(self):
        return reverse("decrement_item_card", kwargs={"id": self.id})


class Order(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True,
                             on_delete=models.SET_NULL, related_name="orders")
    ref_code = models.CharField(
        max_length=100, unique=True)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    order_status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES, blank=True, null=True
    )
    message = models.TextField(blank=True, null=True)
    delivery_method = models.ForeignKey(
        "DeliveryMethod", on_delete=models.SET_NULL, null=True
    )
    payment_option = models.ForeignKey(
        "PaymentOptions", on_delete=models.SET_NULL, null=True
    )
    payment_method = models.ForeignKey(
        "PaymentMethod", on_delete=models.SET_NULL, null=True
    )
    coupon = models.ForeignKey(
        'Coupon', on_delete=models.SET_NULL, blank=True, null=True)
    shipping_address = models.ForeignKey("Address", on_delete=models.SET_NULL, null=True)
    billing_address = models.ForeignKey("Address", related_name="OrdersBailing", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.ref_code} by {self.user} is ordered :{self.ordered}"

    def get_total(self):
        total = 0.0
        for order_item in self.items.all():
            total += float(order_item.get_subtotal())
        return total

    def get_total_coupon(self):
        total = self.get_total()
        if self.coupon:
            total -= self.coupon.amount
        try:
            total += float(self.delivery_method.shipping_price)
        except:
            pass
        return total

    def get_tag_type(self):
        if self.order_status == "ON HOLD":
            return "warning"
        if self.order_status == "PROCESSING":
            return "info"
        if self.order_status == "CANCELED":
            return "secondary"
        if self.order_status == "FAILED":
            return "danger"
        if self.order_status == "COMPLETED":
            return "primary"
        if self.order_status == "REFUNDED":
            return "secondary"

    def get_product_actions(self):
        if self.order_status == "ON HOLD":
            return ["modify", "cancel"]
        elif self.order_status == "PROCESSING":
            return ["modify", "cancel"]
        elif self.order_status == "COMPLETED":
            return ["track", "re-order", "cancel"]
        elif self.order_status == "CANCELED":
            return ["re-order"]
        elif self.order_status == "FAILED":
            return ["re-order"]
        elif self.order_status == "REFUNDED":
            return ["re-order"]


class Coupon(BaseModel):
    code = models.CharField(max_length=20)
    amount = models.FloatField()
    expire_date = models.DateTimeField()

    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"


class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, related_name="addresses")
    full_name = models.CharField(max_length=50)
    societe = models.CharField(max_length=50, blank=True)
    tva = models.CharField(max_length=100, blank=True)
    street_address = models.CharField(max_length=100)
    zip = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50, default="Maroc")
    phone_number = models.CharField(max_length=10)
    default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.full_name} - {self.city}"

    class Meta:
        verbose_name_plural = 'Addresses'


class DeliveryMethod(BaseModel):
    name = models.CharField(max_length=50)
    icon = models.ForeignKey(Image, blank=True, null=True, on_delete=models.SET_NULL)
    description = models.CharField(max_length=100)
    shipping_price = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    payment_options = models.ManyToManyField("PaymentOptions", related_name="delivery_methods")

    def __str__(self):
        return f"{self.name} - {self.shipping_price}"


class PaymentOptions(BaseModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    payment_methods = models.ManyToManyField("PaymentMethod", related_name="payment_options")

    def __str__(self):
        return f"{self.name} - {self.description}"


class PaymentMethod(BaseModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} - {self.description}"


class Contact(BaseModel):
    firstname = models.CharField(max_length=50)
    lastname = models.CharField(max_length=50)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"From {self.firstname} {self.lastname}"


class NewsLetter(BaseModel):
    email = models.EmailField()

    def __str__(self):
        return f"From {self.email}"


class UserProfile(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_profile', on_delete=models.CASCADE,
                             unique=True)
    gender = models.CharField(
        max_length=8,
        choices=GENDER_CHOICES,
    )
    telephone = models.CharField(max_length=10)
    profile_picture = models.OneToOneField(Image, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.ForeignKey(Address, related_name="user_profile", on_delete=models.SET_NULL, null=True,blank=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
