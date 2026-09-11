# Test Output

**The Django test suite (`python manage.py test`) has NOT been executed
in the environment that generated this project**, because that
environment has no outbound network access and Django could not be
installed (`pip install django` and `apt-get install python3-django` both
failed — no route to PyPI or the Ubuntu package mirrors). This is stated
here explicitly rather than fabricating output, per the assignment's own
instructions.

## What was actually verified in this environment

- All 18 Python files in the project were parsed with Python's built-in
  `ast` module and confirmed to be syntactically valid.
- The core recommendation logic in `boxes/packing.py` was manually
  re-implemented with plain Python objects mirroring the Django model
  field names/types (no Django import required) and exercised against
  every scenario also covered by `boxes/tests/test_packing.py`:
  - a product fitting normally,
  - a product fitting only after rotation,
  - a product not fitting in any rotation,
  - weight exceeding box capacity,
  - multiple quantities increasing total weight/volume correctly,
  - an order with multiple different products where one doesn't fit,
  - no suitable box existing,
  - selecting the cheapest box among several that fit,
  - tie-breaking by volume when cost is equal,
  - a multi-product order being matched to a box that fits all items.

  All of these manual checks produced the expected result. This is a
  genuine correctness signal for the algorithm itself, but it is **not**
  a run of the real Django test suite, and does not exercise
  Django-specific behaviour (ORM queries, migrations, the HTTP layer,
  `JsonResponse` status codes, URL routing, etc.).

## How to generate real test output

Run the following locally (or in any environment with internet access to
install Django) and this file's content should be replaced with the
actual terminal output:

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py test
```

Expected test modules that should run:
- `boxes.tests.test_packing` (9 tests)
- `boxes.tests.test_api` (5 tests)
