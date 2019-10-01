from django import forms

from core.models import *


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ('slug', 'product_viewed', 'product_date_available',)
        labels = {'active   ': 'Is Active'}

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

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
