import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from boxes.models import Box, Order, OrderItem, Product


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


class RecommendBoxApiTests(TestCase):
    def test_order_not_found_returns_404(self):
        url = reverse("recommend-box", args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": "Order not found."})

    def test_empty_order_returns_400(self):
        order = Order.objects.create()
        url = reverse("recommend-box", args=[order.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Order has no products."})

    def test_successful_recommendation_returns_box_details(self):
        product = make_product(length=10, width=10, height=10, weight=1)
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)
        cheap_box = make_box(name="Small", length=20, width=20, height=20, cost=5)
        make_box(name="Big", length=40, width=40, height=40, cost=20)

        url = reverse("recommend-box", args=[order.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["recommended_box"]["id"], cheap_box.id)
        self.assertEqual(data["recommended_box"]["name"], "Small")

    def test_no_suitable_box_returns_200_with_null_box_and_message(self):
        product = make_product(length=100, width=100, height=100, weight=1)
        order = Order.objects.create()
        OrderItem.objects.create(order=order, product=product, quantity=1)
        make_box(length=20, width=20, height=20)

        url = reverse("recommend-box", args=[order.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsNone(data["recommended_box"])
        self.assertIn("message", data)

    def test_post_method_not_allowed(self):
        order = Order.objects.create()
        url = reverse("recommend-box", args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)
