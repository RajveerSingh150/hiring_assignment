from decimal import Decimal

from django.test import TestCase

from boxes.models import Box, OrderItem, Order, Product
from boxes.packing import (
    box_can_accommodate,
    order_items_total_volume,
    order_items_total_weight,
    product_fits_in_box,
    recommend_box,
)


def make_product(name="Product", length=10, width=10, height=10, weight=1):
    return Product.objects.create(
        name=name,
        length_cm=Decimal(length),
        width_cm=Decimal(width),
        height_cm=Decimal(height),
        weight_kg=Decimal(weight),
    )


def make_box(name="Box", length=20, width=20, height=20, max_weight=10, cost=5):
    return Box.objects.create(
        name=name,
        internal_length_cm=Decimal(length),
        internal_width_cm=Decimal(width),
        internal_height_cm=Decimal(height),
        max_weight_kg=Decimal(max_weight),
        cost=Decimal(cost),
    )


class ProductFitsInBoxTests(TestCase):
    def test_product_fits_normally(self):
        product = make_product(length=10, width=10, height=10)
        box = make_box(length=20, width=20, height=20)
        self.assertTrue(product_fits_in_box(product, box))

    def test_product_fits_only_after_rotation(self):
        # 30 x 5 x 5 product does not fit in its given orientation in a
        # 10 x 10 x 35 box, but does fit once rotated so the 30cm side
        # aligns with the box's 35cm side.
        product = make_product(length=30, width=5, height=5)
        box = make_box(length=10, width=10, height=35)
        self.assertTrue(product_fits_in_box(product, box))

    def test_product_does_not_fit_in_any_rotation(self):
        product = make_product(length=50, width=50, height=50)
        box = make_box(length=20, width=20, height=20)
        self.assertFalse(product_fits_in_box(product, box))

    def test_product_exactly_matching_dimensions_fits(self):
        product = make_product(length=20, width=20, height=20)
        box = make_box(length=20, width=20, height=20)
        self.assertTrue(product_fits_in_box(product, box))


class BoxCanAccommodateTests(TestCase):
    def test_weight_exceeding_capacity_is_rejected(self):
        product = make_product(length=5, width=5, height=5, weight=100)
        box = make_box(length=20, width=20, height=20, max_weight=10)
        order = Order.objects.create()
        item = OrderItem.objects.create(order=order, product=product, quantity=1)
        self.assertFalse(box_can_accommodate(box, [item]))

    def test_multiple_quantities_increase_total_weight_and_volume(self):
        product = make_product(length=5, width=5, height=5, weight=2)
        order = Order.objects.create()
        item = OrderItem.objects.create(order=order, product=product, quantity=10)

        self.assertEqual(order_items_total_weight([item]), Decimal("20"))
        self.assertEqual(order_items_total_volume([item]), Decimal("1250"))  # 125 * 10

        # A box whose capacity is below the total weight of 10 units must
        # be rejected even though a single unit would fit weight-wise.
        small_capacity_box = make_box(length=50, width=50, height=50, max_weight=15)
        self.assertFalse(box_can_accommodate(small_capacity_box, [item]))

        big_capacity_box = make_box(length=50, width=50, height=50, max_weight=25)
        self.assertTrue(box_can_accommodate(big_capacity_box, [item]))

    def test_multiple_different_products_all_must_individually_fit(self):
        small_product = make_product(name="Small", length=5, width=5, height=5, weight=1)
        oversized_product = make_product(
            name="Oversized", length=100, width=100, height=100, weight=1
        )
        order = Order.objects.create()
        item1 = OrderItem.objects.create(order=order, product=small_product, quantity=1)
        item2 = OrderItem.objects.create(order=order, product=oversized_product, quantity=1)

        box = make_box(length=50, width=50, height=50, max_weight=100)
        # The oversized product alone can never fit, so the box must be
        # rejected even though the small product and total weight are fine.
        self.assertFalse(box_can_accommodate(box, [item1, item2]))


class RecommendBoxTests(TestCase):
    def test_no_suitable_box_returns_none(self):
        product = make_product(length=100, width=100, height=100, weight=1)
        order = Order.objects.create()
        item = OrderItem.objects.create(order=order, product=product, quantity=1)
        box = make_box(length=20, width=20, height=20)

        result = recommend_box([item], [box])
        self.assertIsNone(result)

    def test_selects_cheapest_box_among_multiple_that_fit(self):
        product = make_product(length=10, width=10, height=10, weight=1)
        order = Order.objects.create()
        item = OrderItem.objects.create(order=order, product=product, quantity=1)

        cheap_box = make_box(name="Cheap", length=20, width=20, height=20, cost=5)
        expensive_box = make_box(name="Expensive", length=30, width=30, height=30, cost=15)
        # A box too small to matter for cost comparison, included to make
        # sure it is correctly excluded rather than accidentally chosen.
        too_small_box = make_box(name="TooSmall", length=5, width=5, height=5, cost=1)

        result = recommend_box([item], [too_small_box, expensive_box, cheap_box])
        self.assertEqual(result, cheap_box)

    def test_tie_break_by_smallest_volume_when_cost_equal(self):
        product = make_product(length=10, width=10, height=10, weight=1)
        order = Order.objects.create()
        item = OrderItem.objects.create(order=order, product=product, quantity=1)

        larger_box = make_box(name="Larger", length=30, width=30, height=30, cost=5)
        smaller_box = make_box(name="Smaller", length=20, width=20, height=20, cost=5)

        result = recommend_box([item], [larger_box, smaller_box])
        self.assertEqual(result, smaller_box)

    def test_multiple_products_recommends_a_box_that_fits_all_of_them(self):
        product_a = make_product(name="A", length=10, width=10, height=10, weight=1)
        product_b = make_product(name="B", length=5, width=5, height=20, weight=2)
        order = Order.objects.create()
        item_a = OrderItem.objects.create(order=order, product=product_a, quantity=2)
        item_b = OrderItem.objects.create(order=order, product=product_b, quantity=1)

        box = make_box(length=40, width=40, height=40, max_weight=20, cost=10)

        result = recommend_box([item_a, item_b], [box])
        self.assertEqual(result, box)
