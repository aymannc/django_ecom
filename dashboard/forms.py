from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from core.models import *


class UserForm(UserCreationForm):
    password1 = forms.CharField(label='Mot de pass', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmez le mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            "username", "password1", "password2", "first_name", "last_name",
            "email", "is_active", "is_staff", "is_superuser")
        labels = {
            'username': "Nom d'utilisateur*",
            'first_name': "Prénom*",
            'last_name': "Nom*",
            'is_active': "Active",
            'is_staff': "Staff",
            'is_superuser': "Super utilisateur",

        }
        help_texts = {
            'username': 'Champs obligatoires. 150 caractères ou moins. Lettres, chiffres et @ /. / + / - / _ uniquement.',
            'password2': 'Entrez le même mot de passe qu\'avant, pour vérification',
            'is_active': "Indique si cet utilisateur doit être traité comme actif. Désélectionnez cette option au lieu de supprimer des comptes.",
            'is_staff': "Indique si l'utilisateur peut se connecter à ce site d'administration",
            'is_superuser': "Indique que cet utilisateur dispose de toutes les autorisations sans les attribuer explicitement.",
        }

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control my-3'


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user', 'profile_picture', 'address')
        labels = {
        }

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control my-3'


class OptionForm(forms.ModelForm):
    class Meta:
        model = Product_Options
        fields = "__all__"
        labels = {
            'option_name': "Nom d'option",
        }

    def __init__(self, *args, **kwargs):
        data = {'data-live-search': 'true', 'data-width': '100%',
                'data-style': "btn-primary", 'data-size': "5", 'data-actions-box': "true"}
        super(OptionForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control my-3'
        # self.fields['parent_category'].widget.attrs = self.fields['tags'].widget.attrs = data


class OptionsValuesForm(forms.ModelForm):
    class Meta:
        model = Product_Options_Values
        fields = "__all__"
        labels = {
            'value': "Valeur",
            'price': "Prix",
            'related_option': "Option en relation",
        }

    def __init__(self, *args, **kwargs):
        data = {'data-live-search': 'true', 'data-width': '100%',
                'data-style': "btn-primary", 'data-size': "5", 'data-actions-box': "true"}
        super(OptionsValuesForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control my-3'
        self.fields['related_option'].widget.attrs = data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('slug', 'image')
        labels = {
            'name': 'Nom du catégorie',
            'is_featured': 'Populaire',
            'parent_category': 'Catégorie ',
        }

    def __init__(self, *args, **kwargs):
        data = {'data-live-search': 'true', 'data-width': '100%',
                'data-style': "btn-primary", 'data-size': "5", 'data-actions-box': "true"}
        super(CategoryForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control my-3'
        self.fields['parent_category'].widget.attrs = self.fields['tags'].widget.attrs = data


class AttributesForm(forms.ModelForm):
    class Meta:
        model = Product_attributes
        fields = "__all__"
        labels = {
            'option_value': "Valeur d'option",
        }

    def __init__(self, *args, **kwargs):
        data = {'data-live-search': 'true', 'data-width': '100%',
                'data-style': "btn-primary", 'data-size': "5", 'data-actions-box': "true"}
        super(AttributesForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control my-3'
            visible.field.widget.attrs = data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('slug', 'product_viewed', 'product_date_available', 'additional_options',
                   'product_images')
        labels = {
            'product_name': 'Nom du produit',
            'product_into': 'Informations sur le produit',
            'product_description': 'Description du produit',
            'product_quantity_available': 'Quantité de produit disponible',
            'product_price': 'Prix du produit',
            'product_price_onsale': 'Prix du produit en promo',
            'visible': 'Visible',
            'is_featured': ' Populaire',
            'product_images': 'Images de produits',
            'product_categorie': 'Catégories de produit',
            'related_products': 'Produits similaires',
            'product_attributes': 'Attributs du produit',
            'additional_options': 'options additionelles',
            'tags': 'étiquette',
        }

    def __init__(self, *args, **kwargs):
        data = {'data-live-search': 'true', 'data-width': '100%',
                'data-style': "btn-primary", 'data-size': "5", 'data-actions-box': "true"}
        super(ProductForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control my-3'

        self.fields['tags'].widget.attrs = \
            self.fields['related_products'].widget.attrs = \
            self.fields['product_attributes'].widget.attrs = \
            self.fields['product_categorie'].widget.attrs = data

    # def clean_phone_number(self, exclude=None):
    #     data = self.cleaned_data['phone_number']
    #     if len(data) < 10:
    #         raise forms.ValidationError("phone number should be exactly 10!")
    #     for digit in data:
    #         if digit not in string.digits:
    #             raise forms.ValidationError("Use digits only")
    #     return data
    #
    # def clean_zip(self, exclude=None):
    #     data = self.cleaned_data['zip']
    #     if not len(data) == 5:
    #         raise forms.ValidationError("zip should be exactly 5!")
    #     for digit in data:
    #         if digit not in string.digits:
    #             raise forms.ValidationError("Use digits only")
    #     return data
