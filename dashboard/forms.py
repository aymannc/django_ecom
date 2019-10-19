from django import forms

from core.models import *


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        exclude = ('slug',)
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
        # labels = {
        #     'name': 'Nom du catégorie',
        #     'is_featured': 'Populaire',
        #     'parent_category': 'Catégorie ',
        # }

    def __init__(self, *args, **kwargs):
        data = {'data-live-search': 'true', 'data-width': '100%',
                'data-style': "btn-primary", 'data-size': "5", 'data-actions-box': "true"}
        super(AttributesForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control my-3'
        # self.fields['parent_category'].widget.attrs = self.fields['tags'].widget.attrs = data


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('slug', 'product_viewed', 'product_date_available', 'product_attributes', 'additional_options',
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
            'product_attributes': '1ttributs du produit',
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
