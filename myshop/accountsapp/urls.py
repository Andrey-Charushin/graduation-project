from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView

from .views import (
    RegisterView,
    AboutMeView,
    login_view,
    logout_view

    )

app_name = 'accountsapp'

urlpatterns = [
    path(
        'login/',
        LoginView.as_view(
            template_name="accountsapp/login.html",
            redirect_authenticated_user=True),
            name='login'),

    path('profile/', AboutMeView.as_view(), name='profile'),
    path('register/', RegisterView.as_view(), name='register'),
    path('logout/', logout_view, name='logout'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
