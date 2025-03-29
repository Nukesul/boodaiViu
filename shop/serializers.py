from rest_framework import serializers
from .models import Category, Pizza, Order

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'  # Включает все поля модели Category (id, name)

class PizzaSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True, allow_null=True)  # Поле изображения с полной URL-адресацией
    category_name = serializers.CharField(source='category.name', read_only=True)  # Название категории для удобства

    class Meta:
        model = Pizza
        fields = ['id', 'name', 'category', 'category_name', 'base_price', 'description', 'image', 'stock', 'discount']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'  # Включает все поля модели Order (id, customer_name, address, delivery, comment, total, created_at, items, status)