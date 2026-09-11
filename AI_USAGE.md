# AI Usage

## 1. AI Tool Used

I used Claude through its chat interface to help me build and understand the Django assignment. I provided the assignment requirements in multiple prompts and used Claude mainly for the project structure, implementation, debugging, and test cases.


## 2. Prompt Used

I gave Claude the complete assignment brief in a single prompt. I asked it to build only what was required by the assignment and not add unnecessary features or technologies.

I specifically asked it to:

* Build the complete Django project.
* Keep the implementation simple and understandable.
* Implement the product, box, order, and order-item models.
* Add the box recommendation logic.
* Handle product rotation when checking whether a product fits.
* Handle weight, quantity, and multiple products.
* Provide the required API.
* Add unit and API tests.

## 3. What I Accepted

I accepted most of the basic project structure and implementation because it matched the requirements of the assignment.

This included:

* Django project and app structure.
* `Product`, `Box`, `Order`, and `OrderItem` models.
* Database migration.
* Admin configuration.
* Box recommendation logic in `boxes/packing.py`.
* Rotation-aware dimension checking.
* Weight and quantity handling.
* Cost-based box selection with volume as a tie-breaker.
* The recommendation API and URL.
* Unit tests for the packing logic.
* API tests.

I also kept the project intentionally small. I did not add authentication, Docker, Celery, Redis, a frontend, or unnecessary CRUD endpoints because they were not part of the assignment.

## 4. What I Modified or Rejected

While going through the generated code, I did not just accept everything without checking it.

One important point was the packing logic. The assignment does not define a complete 3D warehouse packing algorithm, so I had to make a reasonable assumption about how multiple products would be handled. I made sure that this assumption was clearly documented instead of presenting the solution as a general 3D bin-packing solution.

Another thing I paid attention to was the API scope. It would have been possible to create separate APIs for creating products, boxes, and orders, but that was unnecessary for this assignment. I kept the API focused on the actual requirement: getting a recommended box for an existing order.

I also made sure that test results were not invented. Claude initially tried to verify the project by running the Django test suite, but Django could not be installed in the sandbox because it had no network access. Therefore, I did not include fake `python manage.py test` output.

## 5. Errors and Problems Faced

There were a few issues and challenges while working on the assignment.

The first major problem was the offline environment. When I tried to install Django using `pip` and also tried installing it through the system package manager, the installation failed because the sandbox could not access the internet. Because of this, I could not run the complete Django test suite inside the sandbox.

Another challenge was understanding the box-fitting logic. At first, comparing the product's length, width, and height directly with the box dimensions seemed straightforward. However, a product can be rotated, so checking only one orientation could incorrectly say that a product does not fit. I had to make sure the implementation considered the different possible orientations.

Handling multiple products and quantities was another part that needed careful checking. It was important not to calculate the order's weight using only one product or ignore the quantity of an item. I specifically checked that quantities contributed correctly to the total weight and the packing calculation.

There was also a design question around selecting a box when multiple boxes could fit. I used cost as the primary selection criterion and volume as a tie-breaker. This gave the recommendation logic a consistent rule instead of simply returning whichever box happened to be encountered first.

## 6. How I Verified the Final Code

Since I could not run the complete Django test suite because Django could not be installed in the offline sandbox, I used several other checks.

I parsed the Python files using Python's `ast` module to check for syntax errors. I also manually compared the migration with the models to make sure the fields and relationships matched.

For the main packing logic, I created simple Python stand-ins for the Django models and tested the recommendation logic separately. I checked cases such as:

* Normal product fit.
* Product fitting after rotation.
* Product not fitting.
* Weight exceeding the box limit.
* Multiple quantities.
* Multiple products.
* No suitable box.
* Multiple suitable boxes.
* Cheapest suitable box.
* Cost tie with volume as the tie-breaker.

The manual checks passed for the scenarios I tested.

However, I have claim that the full Django test suite passed because I actually run `python manage.py test` in the local. The project includes the tests and the README contains the commands needed to run them in a normal Django environment.

The final code was therefore verified as far as the available environment allowed.
