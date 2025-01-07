from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UsernameField

from .models import Profile


class EditProfileForm(forms.ModelForm):
    """Форма для редактирования данных пользователя"""

    about = forms.CharField(widget=forms.Textarea, required=False, label="О себе")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'E-mail',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        profile = kwargs.pop('profile', None)
        super().__init__(*args, **kwargs)

        if profile:
            self.fields['about'].initial = profile.about

    def save(self, commit=True):
        user = super().save(commit)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.about = self.cleaned_data.get('about')
        if commit:
            profile.save()
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Кастомная форма для авторизации"""
    username = UsernameField(label='Имя пользователя', widget=forms.TextInput(attrs={"autofocus": True}))
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )
