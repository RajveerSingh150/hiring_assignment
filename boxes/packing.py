"""
Core box-recommendation logic.

This module is deliberately independent of Django's HTTP layer (no
requests/responses here) so it can be unit tested directly and reused
outside of a view if needed.

Packing approach and its limitations
-------------------------------------
General 3D bin packing (deciding whether an arbitrary set of boxes/items
can be simultaneously arranged inside a container) is NP-hard and is out
of scope for this assignment. Instead, a deliberately simpler and clearly
stated approximation is used:

1. Per-item fit check: every individual unit of every product in the order
   must fit inside the box's internal dimensions in at least one of its 6
   axis-aligned rotations (the product can be placed on its side). If a
   single unit of a product cannot physically fit inside a box in any
   rotation, that box is rejected outright, regardless of remaining space.

2. Aggregate weight check: the summed weight of every unit of every
   product in the order must not exceed the box's maximum weight capacity.

3. Aggregate volume check: the summed volume of every unit of every
   product in the order must not exceed the box's internal volume. This is
   a necessary-but-not-sufficient proxy for "do all these items
   simultaneously fit in the box together" - it does not verify an actual
   3D arrangement of multiple different items packed together, only that
   there is, in principle, enough space and that no single item is too
   large on its own.

This approach will therefore occasionally recommend a box for an order
where a real warehouse worker might struggle to arrange awkwardly-shaped
items together, and conversely can never under-recommend a box that is
physically too small for a single item or too light for the total weight.
This trade-off, and the fact that true multi-item 3D bin packing is not
implemented, is intentional and documented in README.md.
"""
from itertools import permutations
from typing import Iterable, List, Optional


def _rotations(length, width, height):
    """Return the distinct axis-aligned rotations of a l x w x h box."""
    return set(permutations([length, width, height]))


def product_fits_in_box(product, box) -> bool:
    """Return True if a single unit of `product` fits inside `box`'s
    internal dimensions in at least one of its 6 possible rotations."""
    for length, width, height in _rotations(
        product.length_cm, product.width_cm, product.height_cm
    ):
        if (
            length <= box.internal_length_cm
            and width <= box.internal_width_cm
            and height <= box.internal_height_cm
        ):
            return True
    return False


def order_items_total_weight(order_items: Iterable):
    return sum(item.product.weight_kg * item.quantity for item in order_items)


def order_items_total_volume(order_items: Iterable):
    return sum(item.product.volume_cm3 * item.quantity for item in order_items)


def box_can_accommodate(box, order_items: Iterable) -> bool:
    """Return True if `box` can accommodate every item in `order_items`,
    per the approach documented at the top of this module."""
    order_items = list(order_items)

    if order_items_total_weight(order_items) > box.max_weight_kg:
        return False

    for item in order_items:
        if not product_fits_in_box(item.product, box):
            return False

    if order_items_total_volume(order_items) > box.volume_cm3:
        return False

    return True


def recommend_box(order_items: Iterable, boxes: Iterable) -> Optional[object]:
    """Return the most suitable Box for the given order items, or None if
    no box in `boxes` can accommodate them.

    Selection rule (used consistently everywhere a "best" box is chosen):
    among all boxes that can accommodate the order, pick the one with the
    lowest cost. If several boxes share the same lowest cost, the smallest
    (by internal volume) of those is chosen, to keep the choice
    deterministic and to avoid unnecessarily oversized boxes when cost
    alone doesn't distinguish them.
    """
    order_items = list(order_items)

    suitable_boxes: List = [b for b in boxes if box_can_accommodate(b, order_items)]
    if not suitable_boxes:
        return None

    suitable_boxes.sort(key=lambda b: (b.cost, b.volume_cm3))
    return suitable_boxes[0]
