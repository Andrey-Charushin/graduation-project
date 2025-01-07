from django_filters import FilterSet, NumberFilter, ModelChoiceFilter
from .models import Product, Category
from django.db.models import Avg

class ProductFilter(FilterSet):
    price_min = NumberFilter(field_name='price', lookup_expr='gte', label='Цена мин.')
    price_max = NumberFilter(field_name='price', lookup_expr='lte', label='Цена макс.')
    category = ModelChoiceFilter(queryset=Category.objects.all(), label='Категория')
    rating_min = NumberFilter(method='filter_by_average_rating', label='Мин рейтинг')

    class Meta:
        model = Product
        fields = ['price_min', 'price_max', 'category', 'rating_min']

    def filter_by_average_rating(self, queryset, name, value):
        """Фильтрует продукты по минимальному среднему рейтингу."""
        return queryset.annotate(average_rating=Avg('review__rating')).filter(average_rating__gte=value)
