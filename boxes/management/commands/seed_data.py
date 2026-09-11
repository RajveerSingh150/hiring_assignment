"""
Management command that creates dummy data for every field in the
boxes app (Product, Box, Order, OrderItem), so the app and its API can be
exercised manually after `python manage.py migrate`.

Usage:
    python manage.py seed_data
    python manage.py seed_data --flush   # wipe existing boxes-app data first

The scenarios created deliberately cover the cases the recommendation
logic is meant to handle, so you can hit the API and see varied results:
    - Order 1: single small product, normal fit, multiple boxes qualify
      (cheapest should be picked).
    - Order 2: a long/thin product that only one box is long enough for.
    - Order 3: a product too heavy for every box (no suitable box).
    - Order 4: a product too large for every box in any rotation
      (no suitable box).
    - Order 5: multiple different products with multiple quantities.
    - Order 6: an order with no items (empty order edge case).
    - Order 7: a product that only fits once rotated onto a different face.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from boxes.models import Box, Order, OrderItem, Product


class Command(BaseCommand):
    help = "Seed the database with dummy Products, Boxes, Orders and OrderItems."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete all existing Product/Box/Order/OrderItem rows before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            OrderItem.objects.all().delete()
            Order.objects.all().delete()
            Product.objects.all().delete()
            Box.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing boxes-app data deleted."))

        # ------------------------------------------------------------------
        # Boxes: a range of sizes/costs so the "cheapest that fits" rule has
        # something interesting to choose between.
        # ------------------------------------------------------------------
        small_box = Box.objects.create(
            name="Small Box",
            internal_length_cm=Decimal("20.00"),
            internal_width_cm=Decimal("15.00"),
            internal_height_cm=Decimal("10.00"),
            max_weight_kg=Decimal("3.00"),
            cost=Decimal("2.50"),
        )
        medium_box = Box.objects.create(
            name="Medium Box",
            internal_length_cm=Decimal("35.00"),
            internal_width_cm=Decimal("25.00"),
            internal_height_cm=Decimal("20.00"),
            max_weight_kg=Decimal("10.00"),
            cost=Decimal("5.00"),
        )
        large_box = Box.objects.create(
            name="Large Box",
            internal_length_cm=Decimal("50.00"),
            internal_width_cm=Decimal("40.00"),
            internal_height_cm=Decimal("35.00"),
            max_weight_kg=Decimal("20.00"),
            cost=Decimal("9.00"),
        )
        long_narrow_box = Box.objects.create(
            name="Long Narrow Box",
            internal_length_cm=Decimal("60.00"),
            internal_width_cm=Decimal("10.00"),
            internal_height_cm=Decimal("10.00"),
            max_weight_kg=Decimal("5.00"),
            cost=Decimal("4.00"),
        )
        self.stdout.write(self.style.SUCCESS(
            f"Created 4 boxes: {small_box.name}, {medium_box.name}, "
            f"{large_box.name}, {long_narrow_box.name}"
        ))

        # ------------------------------------------------------------------
        # Products: normal, needs-rotation, too heavy, too large.
        # ------------------------------------------------------------------
        mug = Product.objects.create(
            name="Coffee Mug",
            length_cm=Decimal("10.00"),
            width_cm=Decimal("10.00"),
            height_cm=Decimal("9.00"),
            weight_kg=Decimal("0.40"),
        )
        book = Product.objects.create(
            name="Hardcover Book",
            length_cm=Decimal("23.00"),
            width_cm=Decimal("15.00"),
            height_cm=Decimal("3.00"),
            weight_kg=Decimal("0.80"),
        )
        # Long and thin: only the "Long Narrow Box" (60 x 10 x 10) has a
        # side long enough for this, so it demonstrates the fit check
        # correctly ruling out every box whose longest side is under 55cm.
        curtain_rod = Product.objects.create(
            name="Curtain Rod",
            length_cm=Decimal("55.00"),
            width_cm=Decimal("8.00"),
            height_cm=Decimal("8.00"),
            weight_kg=Decimal("1.20"),
        )
        # Too heavy for any box on its own.
        dumbbell = Product.objects.create(
            name="Dumbbell",
            length_cm=Decimal("30.00"),
            width_cm=Decimal("12.00"),
            height_cm=Decimal("12.00"),
            weight_kg=Decimal("25.00"),
        )
        # Too large in every rotation for any box.
        wardrobe_door = Product.objects.create(
            name="Wardrobe Door",
            length_cm=Decimal("200.00"),
            width_cm=Decimal("60.00"),
            height_cm=Decimal("3.00"),
            weight_kg=Decimal("18.00"),
        )
        t_shirt = Product.objects.create(
            name="T-Shirt",
            length_cm=Decimal("30.00"),
            width_cm=Decimal("20.00"),
            height_cm=Decimal("2.00"),
            weight_kg=Decimal("0.20"),
        )
        # Declared as 30 x 5 x 22: in that exact orientation the height
        # (22cm) exceeds the Medium Box's 20cm internal height, but once
        # rotated to lie as 30 x 22 x 5 it fits (30<=35, 22<=25, 5<=20).
        # This is a genuine "only fits after rotation" example.
        picture_frame = Product.objects.create(
            name="Picture Frame",
            length_cm=Decimal("30.00"),
            width_cm=Decimal("5.00"),
            height_cm=Decimal("22.00"),
            weight_kg=Decimal("1.50"),
        )
        self.stdout.write(self.style.SUCCESS(
            f"Created 7 products: {mug.name}, {book.name}, {curtain_rod.name}, "
            f"{dumbbell.name}, {wardrobe_door.name}, {t_shirt.name}, "
            f"{picture_frame.name}"
        ))

        # ------------------------------------------------------------------
        # Orders covering the scenarios described in the module docstring.
        # ------------------------------------------------------------------
        order_1 = Order.objects.create()
        OrderItem.objects.create(order=order_1, product=mug, quantity=1)

        order_2 = Order.objects.create()
        OrderItem.objects.create(order=order_2, product=curtain_rod, quantity=1)

        order_3 = Order.objects.create()
        OrderItem.objects.create(order=order_3, product=dumbbell, quantity=1)

        order_4 = Order.objects.create()
        OrderItem.objects.create(order=order_4, product=wardrobe_door, quantity=1)

        order_5 = Order.objects.create()
        OrderItem.objects.create(order=order_5, product=mug, quantity=2)
        OrderItem.objects.create(order=order_5, product=book, quantity=1)
        OrderItem.objects.create(order=order_5, product=t_shirt, quantity=5)

        order_6 = Order.objects.create()  # intentionally empty

        order_7 = Order.objects.create()
        OrderItem.objects.create(order=order_7, product=picture_frame, quantity=1)

        self.stdout.write(self.style.SUCCESS("Created 7 orders."))
        self.stdout.write("")
        self.stdout.write(self.style.MIGRATE_HEADING("Try the API for each order:"))
        for order, description in [
            (order_1, "single small product, normal fit -> expect Small Box"),
            (order_2, "long/thin product -> expect Long Narrow Box"),
            (order_3, "product too heavy for every box -> expect no suitable box"),
            (order_4, "product too large for every box -> expect no suitable box"),
            (order_5, "multiple products/quantities -> expect a box fitting all"),
            (order_6, "empty order -> expect 400 error"),
            (order_7, "product only fits after rotation -> expect Medium Box"),
        ]:
            self.stdout.write(
                f"  GET /api/orders/{order.id}/recommend-box/   ({description})"
            )
