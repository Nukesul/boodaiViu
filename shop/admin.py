from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Sum
import json
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from .models import Category, Pizza, Order

# Кастомизация стандартного admin.site
admin.site.site_header = "Админ-панель Booay Pizza"
admin.site.site_title = "Booay Pizza"
admin.site.index_title = "Управление пиццерией"

class CustomAdminMixin:
    class Media:
        css = {'all': ('admin/css/output.css',)}
        js = ('admin/js/my_custom_admin.js',)

@admin.register(Category)
class CategoryAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'pizza_count', 'total_stock', 'total_value', 'category_link')
    search_fields = ('name',)
    actions = ['duplicate_categories', 'merge_categories']
    list_per_page = 20
    ordering = ('name',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            pizza_count=Count('pizza'),
            total_stock=Sum('pizza__stock'),
            total_value=Sum('pizza__base_price')
        )

    def pizza_count(self, obj):
        return obj.pizza_count
    pizza_count.short_description = "Количество пицц"

    def total_stock(self, obj):
        return obj.total_stock or 0
    total_stock.short_description = "Общий запас"

    def total_value(self, obj):
        return f"${obj.total_value or 0:.2f}"
    total_value.short_description = "Общая стоимость"

    def category_link(self, obj):
        url = reverse('admin:shop_pizza_changelist') + f'?category__id__exact={obj.id}'
        return format_html('<a href="{}">Посмотреть пиццы</a>', url)
    category_link.short_description = "Ссылка"

    def duplicate_categories(self, request, queryset):
        for category in queryset:
            category.pk = None
            category.name += " (копия)"
            category.save()
        self.message_user(request, f"Созданы копии для {queryset.count()} категорий.")
    duplicate_categories.short_description = "Дублировать выбранные категории"

    def merge_categories(self, request, queryset):
        if queryset.count() < 2:
            self.message_user(request, "Выберите как минимум 2 категории для объединения.", level=messages.ERROR)
            return
        main_category = queryset.first()
        other_categories = queryset.exclude(id=main_category.id)
        pizzas = Pizza.objects.filter(category__in=other_categories)
        pizzas.update(category=main_category)
        other_categories.delete()
        self.message_user(request, f"Объединено {other_categories.count()} категорий в '{main_category.name}'.")
    merge_categories.short_description = "Объединить выбранные категории"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].label = "Название"
        return form

@admin.register(Pizza)
class PizzaAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'stock', 'display_image', 'is_available', 'discount', 'final_price')
    list_filter = ('category', 'stock', 'discount')
    search_fields = ('name', 'description')
    list_editable = ('base_price', 'stock', 'discount')
    actions = ['set_stock_to_zero', 'increase_price', 'decrease_price', 'apply_discount', 'remove_discount', 'export_to_csv']
    prepopulated_fields = {'description': ('name',)}
    list_per_page = 20
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'base_price', 'description', 'image', 'stock', 'discount')
        }),
    )
    ordering = ('name',)

    def display_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.image.url)
        return "Нет изображения"
    display_image.short_description = "Изображение"

    def is_available(self, obj):
        return obj.stock > 0
    is_available.boolean = True
    is_available.short_description = "В наличии"

    def final_price(self, obj):
        if obj.discount:
            return f"${(obj.base_price * (100 - obj.discount) / 100):.2f}"
        return f"${obj.base_price:.2f}"
    final_price.short_description = "Итоговая цена"

    def set_stock_to_zero(self, request, queryset):
        updated = queryset.update(stock=0)
        self.message_user(request, f"Обновлено {updated} пицц: запас установлен в 0")
    set_stock_to_zero.short_description = "Установить запас в 0"

    def increase_price(self, request, queryset):
        for pizza in queryset:
            pizza.base_price *= 1.1
            pizza.save()
        self.message_user(request, f"Цены увеличены на 10 процентов для {queryset.count()} пицц")
    increase_price.short_description = "Увеличить цену на 10 процентов"

    def decrease_price(self, request, queryset):
        for pizza in queryset:
            pizza.base_price *= 0.9
            pizza.save()
        self.message_user(request, f"Цены уменьшены на 10 процентов для {queryset.count()} пицц")
    decrease_price.short_description = "Уменьшить цену на 10 процентов"

    def apply_discount(self, request, queryset):
        updated = queryset.update(discount=10)
        self.message_user(request, f"Скидка 10 процентов применена к {updated} пиццам")
    apply_discount.short_description = "Применить скидку 10 процентов"

    def remove_discount(self, request, queryset):
        updated = queryset.update(discount=0)
        self.message_user(request, f"Скидка снята с {updated} пицц")
    remove_discount.short_description = "Снять скидку"

    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="pizzas_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Название', 'Категория', 'Базовая цена', 'Запас', 'Скидка', 'Итоговая цена'])
        for pizza in queryset:
            final_price = pizza.base_price * (100 - pizza.discount) / 100 if pizza.discount else pizza.base_price
            writer.writerow([
                pizza.id,
                pizza.name,
                pizza.category.name,
                pizza.base_price,
                pizza.stock,
                pizza.discount,
                final_price
            ])
        return response
    export_to_csv.short_description = "Экспортировать в CSV"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].label = "Название"
        form.base_fields['category'].label = "Категория"
        form.base_fields['base_price'].label = "Базовая цена"
        form.base_fields['description'].label = "Описание"
        form.base_fields['image'].label = "Изображение"
        form.base_fields['stock'].label = "Запас"
        form.base_fields['discount'].label = "Скидка (проценты)"
        return form

@admin.register(Order)
class OrderAdmin(CustomAdminMixin, admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'total', 'delivery', 'status', 'created_at', 'item_count', 'view_items')
    list_filter = ('delivery', 'status', 'created_at')
    search_fields = ('customer_name', 'address', 'comment')
    readonly_fields = ('created_at',)
    actions = ['mark_as_express', 'mark_as_shipped', 'mark_as_delivered', 'cancel_orders', 'export_to_csv']
    fields = ('customer_name', 'address', 'delivery', 'comment', 'total', 'status', 'created_at', 'items')
    date_hierarchy = 'created_at'
    list_per_page = 20
    ordering = ('-created_at',)

    def item_count(self, obj):
        try:
            items = json.loads(obj.items) if obj.items else []
            return len(items)
        except (json.JSONDecodeError, TypeError):
            return len(obj.items.split(',')) if obj.items and isinstance(obj.items, str) and obj.items.strip() else 0
    item_count.short_description = "Пицц в заказе"

    def view_items(self, obj):
        try:
            items = json.loads(obj.items) if obj.items else []
            if not items:
                return "Нет пицц"
            item_list = "<ul>"
            for item in items:
                if isinstance(item, dict) and 'name' in item:
                    item_list += f"<li>{item['name']} (x{item.get('quantity', 1)})</li>"
                else:
                    item_list += f"<li>{item}</li>"
            item_list += "</ul>"
            return mark_safe(item_list)
        except (json.JSONDecodeError, TypeError):
            return obj.items or "Нет пицц"
    view_items.short_description = "Пиццы"

    def mark_as_express(self, request, queryset):
        updated = queryset.update(delivery='express')
        self.message_user(request, f"Обновлено {updated} заказов: доставка изменена на Экспресс")
    mark_as_express.short_description = "Пометить как Экспресс"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status='Shipped')
        self.message_user(request, f"Обновлено {updated} заказов: статус изменён на 'Отправлен'")
    mark_as_shipped.short_description = "Пометить как отправленные"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='Delivered')
        self.message_user(request, f"Обновлено {updated} заказов: статус изменён на 'Доставлен'")
    mark_as_delivered.short_description = "Пометить как доставленные"

    def cancel_orders(self, request, queryset):
        updated = queryset.update(status='Cancelled')
        self.message_user(request, f"Обновлено {updated} заказов: статус изменён на 'Отменён'")
    cancel_orders.short_description = "Отменить заказы"

    def export_to_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['ID', 'Клиент', 'Итого', 'Тип доставки', 'Статус', 'Дата создания', 'Пиццы'])
        for order in queryset:
            writer.writerow([
                order.id,
                order.customer_name,
                order.total,
                order.delivery,
                order.status,
                order.created_at,
                order.items
            ])
        return response
    export_to_csv.short_description = "Экспортировать в CSV"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['items'].widget = admin.widgets.AdminTextareaWidget(attrs={'rows': 5, 'cols': 50})
        form.base_fields['items'].help_text = "Перечислите пиццы в формате JSON или через запятую, например: Pizza1, Pizza2, Pizza3"
        form.base_fields['customer_name'].label = "Имя клиента"
        form.base_fields['address'].label = "Адрес"
        form.base_fields['delivery'].label = "Тип доставки"
        form.base_fields['comment'].label = "Комментарий"
        form.base_fields['total'].label = "Итого"
        form.base_fields['status'].label = "Статус"
        form.base_fields['created_at'].label = "Дата создания"
        form.base_fields['items'].label = "Пиццы"
        return form