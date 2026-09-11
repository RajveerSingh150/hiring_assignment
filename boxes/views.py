from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .models import Box, Order
from .packing import recommend_box


@require_GET
def recommend_box_view(request, order_id):
    """GET /api/orders/<order_id>/recommend-box/

    Returns the recommended shipping box for the given order, or a
    descriptive error/message for the documented edge cases.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return JsonResponse({"error": "Order not found."}, status=404)

    order_items = list(order.items.select_related("product").all())

    if not order_items:
        return JsonResponse({"error": "Order has no products."}, status=400)

    boxes = Box.objects.all()
    box = recommend_box(order_items, boxes)

    if box is None:
        return JsonResponse(
            {
                "order_id": order.id,
                "recommended_box": None,
                "message": "No available box can accommodate this order.",
            },
            status=200,
        )

    return JsonResponse(
        {
            "order_id": order.id,
            "recommended_box": {
                "id": box.id,
                "name": box.name,
                "internal_length_cm": float(box.internal_length_cm),
                "internal_width_cm": float(box.internal_width_cm),
                "internal_height_cm": float(box.internal_height_cm),
                "max_weight_kg": float(box.max_weight_kg),
                "cost": float(box.cost),
            },
        },
        status=200,
    )
