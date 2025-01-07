from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, PasswordChangeDoneView, PasswordChangeView

from .views import (
    RegisterView,
    AboutMeView,
    edit_profile,
    logout_view,

)
from .forms import CustomAuthenticationForm

app_name = 'accountsapp'

urlpatterns = [
                  path(
                      'login/',
                      LoginView.as_view(
                          authentication_form=CustomAuthenticationForm,
                          template_name="accountsapp/login.html",
                          redirect_authenticated_user=True),
                      name='login'),

                  path('profile/', AboutMeView.as_view(), name='profile'),
                  path('profile/edit', edit_profile, name='edit_profile'),
                  path('register/', RegisterView.as_view(), name='register'),
                  path('password-change/', PasswordChangeView.as_view(
                      template_name='accountsapp/password_change.html',
                      success_url='/accounts/password-change/done/'
                  ), name='password_change'),
                  path('password-change/done/', PasswordChangeDoneView.as_view(
                      template_name='accountsapp/password_change_done.html'
                  ), name='password_change_done'),
                  path('logout/', logout_view, name='logout'),

              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
