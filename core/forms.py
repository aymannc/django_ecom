import string

from allauth.account.forms import LoginForm
from django import forms

from .models import *

GENDER_CHOICES = [
    ('F', 'Female'),
    ('M', 'Male'),
]


class CouponForm(forms.ModelForm):
    code = forms.CharField(max_length=20, label='')

    class Meta:
        model = Coupon
        fields = ("code",)


class MessageForm(forms.ModelForm):
    message = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2, 'cols': 40}), label='')

    class Meta:
        model = Order
        fields = ("message",)


class MyLoginForm(LoginForm):
    def __init__(self, *args, **kwargs):
        super(MyLoginForm, self).__init__(*args, **kwargs)
        self.fields['login'].widget = forms.TextInput(attrs={'type': 'email', 'class': 'form-control'})
        self.fields['password'].widget = forms.PasswordInput(attrs={'class': 'form-control'})


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        labels = {
            'full_name': "Nom *",
            'street_address': "Adresse *",
            'societe': "Prénom *",
            'city': "Ville *",
            'state': "Région *",
            'country': "Pays *",
            'phone_number': "Téléphone *",
        }
        exclude = ('user', 'default',)

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    def clean_phone_number(self, exclude=None):
        data = self.cleaned_data['phone_number']
        if len(data) < 10:
            raise forms.ValidationError("phone number should be exactly 10!")
        for digit in data:
            if digit not in string.digits:
                raise forms.ValidationError("Use digits only")
        return data

    def clean_zip(self, exclude=None):
        data = self.cleaned_data['zip']
        if not len(data) == 5:
            raise forms.ValidationError("zip should be exactly 5!")
        for digit in data:
            if digit not in string.digits:
                raise forms.ValidationError("Use digits only")
        return data


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['message'].widget = forms.Textarea(attrs={'rows': 4, 'cols': 40})
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class NewsLetterEmailForm(forms.ModelForm):
    class Meta:
        model = NewsLetterEmail
        fields = ('email',)


class UserProfileForm(forms.Form):
    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={'style': ' padding : 0px 20px'}),
    )
    firstname = forms.CharField(max_length=50)
    lastname = forms.CharField(max_length=50)
    telephone = forms.CharField(max_length=10)
    email = forms.EmailField(max_length=30)

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)
