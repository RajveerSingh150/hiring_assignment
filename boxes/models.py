from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models


class Product(models.Model):
    """A sellable product with physical dimensions and weight.

    All dimensions are stored in centimetres and weight in kilograms.
    Using a single consistent unit across the whole project avoids unit
    conversion bugs and keeps the recommendation logic simple.
    """

    name = models.CharField(max_length=255)
    length_cm = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    width_cm = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    height_cm = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    weight_kg = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )

    def __str__(self):
        return self.name

    @property
    def volume_cm3(self):
        return self.length_cm * self.width_cm * self.height_cm


class Box(models.Model):
    """A shipping box available to the warehouse.

    Dimensions describe the *internal* usable space of the box (i.e. the
    space actually available to place products in), since that is what
    matters for a packing decision.
    """

    name = models.CharField(max_length=255)
    internal_length_cm = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    internal_width_cm = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    internal_height_cm = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    max_weight_kg = models.DecimalField(
        max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)]
    )
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, validators=[MinValueValidator(0)]
    )

    def __str__(self):
        return self.name

    @property
    def volume_cm3(self):
        return self.internal_length_cm * self.internal_width_cm * self.internal_height_cm


class Order(models.Model):
    """A customer order. Products are attached via OrderItem."""

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    """A line item in an order: a product and the quantity ordered."""

    order = models.ForeignKey(Order, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name="order_items", on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    def clean(self):
        if self.quantity < 1:
            raise ValidationError("Quantity must be at least 1.")

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
