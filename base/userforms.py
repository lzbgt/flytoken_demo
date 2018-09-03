from .models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import ugettext as _
from .models import Profile
import re

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='*', label=_('邮箱'),
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('邮箱')}), required=True
                             )
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=True ,attrs={'class': 'form-control', 'placeholder': _('密码'), 'required': 'required'}), label="密码")
    rcode = forms.CharField(max_length=254, help_text='(选填)', label="推荐码",required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('推荐码'),}))

    def __init__(self,*args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        del self.fields['password2']
    class Meta:
        model = User
        fields = ('email', 'password1', 'rcode')

    def clean_email(self):
        # Get the email
        email = self.cleaned_data.get('email')
        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return email

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError( "用户已经存在")


    def clean_username(self):
        # Get the username
        username = self.cleaned_data.get('username')

        # Check to see if any users already exist with this email as a username.
        try:
            match = User.objects.get(username=username)
        except User.DoesNotExist:
            # Unable to find a user, this is fine
            return username

        # A user was found with this as a username, raise an error.
        raise forms.ValidationError("用户已经存在")

    def clean_rcode(self):
        rcode = self.cleaned_data.get('rcode')
        if rcode == None or rcode == '':
            return ''
        ids, _ = Profile.get_referres(rcode)
        if ids is None:
            raise forms.ValidationError("非法推荐码")
        return rcode

    def clean_password1(self):
        password1=self.cleaned_data.get('password1')
        if re.match(r'\w{6,32}', password1) is None:
            raise forms.ValidationError("弱密码")
        return password1

    def clean_password2(self):
        return self.password1