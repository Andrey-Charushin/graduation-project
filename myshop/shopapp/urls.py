from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import product_detail

appname = 'shopapp'

urlpatterns = [
    path('product/<int:product_id>/', product_detail, name='product_detail'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
