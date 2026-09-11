# AI-Assisted Box Selection System

A small Django application that recommends the most suitable shipping box
for an order, based on product dimensions/weight and box internal
dimensions/weight capacity/cost.

## Project overview

- `Product` — a sellable item with length/width/height (cm) and weight (kg).
- `Box` — a shipping box with internal length/width/height (cm), maximum
  weight capacity (kg), and cost.
- `Order` / `OrderItem` — an order is a collection of `(product, quantity)`
  line items.
- `boxes/packing.py` — the recommendation logic, kept independent of the
  HTTP layer so it can be unit tested directly.
- `boxes/views.py` — a single JSON API endpoint that recommends a box for
  a given order, using the logic in `packing.py`.

## Setup instructions

### 1. Create a virtual environment (recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run migrations

```bash
python manage.py migrate
```

### 4. Run the application

```bash
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

To try it out you'll need some data. The easiest way is the Django admin:

```bash
python manage.py createsuperuser
python manage.py runserver
# then visit http://127.0.0.1:8000/admin/ and add Products, Boxes, an
# Order, and OrderItems
```

Alternatively, use `python manage.py shell` to create objects directly via
the ORM.

### 4b. (Optional) Seed dummy data

A management command is included to populate the database with sample
Products, Boxes, and Orders covering the main scenarios (normal fit,
fits-only-after-rotation, too heavy, too large, multiple items/quantities,
empty order):

```bash
python manage.py seed_data
# or, to wipe existing data first:
python manage.py seed_data --flush
```

It prints the order IDs it created along with the API URL to try for
each one.

### 5. Run tests

```bash
python manage.py test
```

## API endpoint

### `GET /api/orders/<order_id>/recommend-box/`

Recommends a box for the given order.

**Example request:**

```
GET /api/orders/1/recommend-box/
```

**Example response — success:**

```json
{
  "order_id": 1,
  "recommended_box": {
    "id": 2,
    "name": "Medium Box",
    "internal_length_cm": 30.0,
    "internal_width_cm": 20.0,
    "internal_height_cm": 15.0,
    "max_weight_kg": 10.0,
    "cost": 8.5
  }
}
```

**Example response — no suitable box found** (HTTP 200; this is a valid
business outcome, not a client error):

```json
{
  "order_id": 1,
  "recommended_box": null,
  "message": "No available box can accommodate this order."
}
```

**Example response — order not found** (HTTP 404):

```json
{
  "error": "Order not found."
}
```

**Example response — order has no products** (HTTP 400):

```json
{
  "error": "Order has no products."
}
```

Only `GET` is supported; any other HTTP method returns `405 Method Not
Allowed`.

## Data model

- `Product(name, length_cm, width_cm, height_cm, weight_kg)`
- `Box(name, internal_length_cm, internal_width_cm, internal_height_cm, max_weight_kg, cost)`
- `Order(created_at)`
- `OrderItem(order → Order, product → Product, quantity)`

All physical dimensions are stored in centimetres and all weights in
kilograms, consistently across the whole project, to avoid unit-mismatch
bugs.

## Recommendation algorithm

Implemented in `boxes/packing.py`. General 3D bin packing (finding whether
an arbitrary set of differently-shaped items can be simultaneously
arranged inside a container) is NP-hard and is **not** implemented here.
Instead, a clearly-defined, simpler approximation is used:

1. **Per-item fit check.** Every individual unit of every product in the
   order must fit inside a candidate box's internal dimensions in at least
   one of its 6 axis-aligned rotations (the product may be placed on any
   side). If a single unit of any product cannot physically fit inside a
   box in any rotation, that box is rejected outright.
2. **Aggregate weight check.** The summed weight of every unit of every
   product in the order must not exceed the box's maximum weight capacity.
3. **Aggregate volume check.** The summed volume of every unit of every
   product in the order must not exceed the box's internal volume. This is
   a *necessary but not sufficient* stand-in for "do all these items
   simultaneously fit together" — it does not simulate an actual 3D
   arrangement of multiple different items packed together in the same
   box, only that there is, in principle, enough total space and that no
   single item is individually too large.

A box is considered suitable for an order only if it passes all three
checks.

**Box selection rule** (used consistently wherever a "best" box needs to
be picked): among all suitable boxes, the one with the **lowest cost** is
chosen. If multiple suitable boxes share the same lowest cost, the one
with the **smallest internal volume** among them is chosen, to keep the
result deterministic and avoid recommending an unnecessarily large box
when cost doesn't distinguish the options.

## Assumptions and limitations

- **Unit system:** all lengths in centimetres, all weights in kilograms.
  Not specified by the assignment, so this was a necessary decision.
- **"Internal dimensions"**: `Box` dimensions represent internal usable
  space (what products actually need to fit into), not external box
  dimensions or wall thickness. Wall thickness is out of scope.
- **No true multi-item 3D bin packing.** As explained above, the
  volume-sum + per-item-fit approach is a reasonable, explicitly
  documented approximation, not a guarantee of a real physical
  arrangement for complex multi-item orders. For a single product type
  (even in large quantity) or orders with only a couple of items, this
  approximation is generally reliable; it becomes weaker as the number of
  differently-shaped items in one order grows.
- **Rotation model:** only axis-aligned rotations (6 orientations per
  item) are considered — no diagonal/tilted placements.
- **"No suitable box" is a 200, not an error status.** It's a valid
  business result (the warehouse genuinely has no box that works), so the
  API returns HTTP 200 with `"recommended_box": null` plus a `message`,
  rather than a 4xx/5xx error.
- **Database:** SQLite is used for simplicity, appropriate for this
  assignment's scope; nothing in the code is SQLite-specific.
- **No authentication/authorization** was implemented, since the
  assignment does not request it and it isn't needed to demonstrate the
  recommendation logic.
- **No CRUD API for Products/Boxes/Orders** was built. The assignment's
  focus is the box-recommendation logic; data can be entered through the
  Django admin (`/admin/`) or the ORM. Only the recommendation endpoint is
  exposed as an API, to avoid building unrequested functionality.
- **Products with a zero or negative dimension/weight are rejected** via
  model-level `MinValueValidator`s, since such values are physically
  meaningless.
