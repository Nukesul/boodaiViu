from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Pizza(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Базовая цена пиццы")
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='pizzas/', null=True, blank=True)
    stock = models.IntegerField(default=0)
    discount = models.IntegerField(default=0, help_text="Скидка в процентах (0-100)")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Ожидает обработки'),
        ('Shipped', 'Отправлен'),
        ('Delivered', 'Доставлен'),
        ('Cancelled', 'Отменён'),
    )
    customer_name = models.CharField(max_length=200)
    address = models.TextField()
    delivery = models.CharField(max_length=50, choices=[('standard', 'Standard'), ('express', 'Express'), ('pickup', 'Pickup')])
    comment = models.TextField(blank=True, null=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    items = models.TextField(default='', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"Order {self.id} by {self.customer_name}"

    class Meta:
        ordering = ['-created_at']