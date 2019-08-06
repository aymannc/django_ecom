from allauth.account.forms import LoginForm
from django import forms

from .models import *


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
        exclude = ('user', 'default',)

    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'

    def clean_phone_number(self, exclude=None):
        data = self.cleaned_data['phone_number']
        if len(data) < 10:
            raise forms.ValidationError("phone number should be exactly 10!")
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


class NewsLetterForm(forms.ModelForm):
    email = forms.EmailField(max_length=50, label='Votre adresse email')

    class Meta:
        model = NewsLetter
        fields = "__all__"


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('image',)
