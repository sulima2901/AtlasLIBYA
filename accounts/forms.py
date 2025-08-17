from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="كلمة المرور")
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="تأكيد كلمة المرور")

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('البريد الإلكتروني مستخدم بالفعل.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password != password_confirm:
            raise ValidationError("كلمة المرور غير متطابقة.")
        if password and len(password) < 8:
            raise ValidationError("كلمة المرور يجب أن تكون 8 أحرف على الأقل.")
        return cleaned_data

class LoginForm(forms.Form):
    username_or_email = forms.CharField(label="اسم المستخدم أو البريد الإلكتروني")
    password = forms.CharField(widget=forms.PasswordInput, label="كلمة المرور")