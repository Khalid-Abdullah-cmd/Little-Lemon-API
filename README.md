# Restaurant Menu & Ordering API

A RESTful backend built with **Django** and **Django REST Framework** for managing a restaurant's menu, customer carts, and orders. It supports role-based access for three kinds of users (customers, delivery crew, and managers), along with filtering, searching, ordering, pagination, and request throttling.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [User Roles & Permissions](#user-roles--permissions)
- [API Reference](#api-reference)
- [Filtering, Searching, Ordering & Pagination](#filtering-searching-ordering--pagination)
- [Data Models](#data-models)
- [Project Structure](#project-structure)
- [Known Notes](#known-notes)

---

## Features

- **Menu management**: managers can create, update, and delete menu items; everyone can browse them.
- **Role-based access control**: Manager, Delivery crew, and Customer roles, enforced through Django groups and custom DRF permission classes.
- **Group management**: managers can promote or remove users from the Manager and Delivery crew groups.
- **Shopping cart**: authenticated users can add items, increase quantities, and empty their cart.
- **Order workflow**: placing an order converts the cart into an order with line items, then clears the cart. Managers assign delivery crew, and crew update delivery status.
- **Query tools**: category filtering, title search, and custom ordering on menu items; status filtering and ordering on orders.
- **Pagination and throttling** on all key endpoints.

## Tech Stack

- Python 3
- Django
- Django REST Framework

## Getting Started

### 1. Clone and install

```bash
git clone <your-repo-url>
cd <your-project-folder>

python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

pip install django djangorestframework
```

### 2. Apply migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create a superuser

```bash
python manage.py createsuperuser
```

### 4. Create the required user groups

The API relies on two Django groups. Create them (exact names, case-sensitive) in the admin panel at `/admin/` or via the shell:

```python
from django.contrib.auth.models import Group
Group.objects.get_or_create(name="Manager")
Group.objects.get_or_create(name="Delivery crew")
```

Then add your first user to the **Manager** group through the admin panel so they can manage everyone else.

### 5. Configure throttling

The views use DRF's `AnonRateThrottle` and `UserRateThrottle`, so define rates in your `settings.py`:

```python
REST_FRAMEWORK = {
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",
        "user": "60/minute",
    },
}
```

You will also need an authentication method configured for DRF (for example, token authentication) so clients can identify themselves.

### 6. Run the server

```bash
python manage.py runserver
```

## User Roles & Permissions

| Role | Description |
|------|-------------|
| **Anonymous** | Can browse the menu (read-only). |
| **Customer** | Any authenticated user who is not in a group. Manages their own cart and orders. |
| **Delivery crew** | Can view orders assigned to them and update their delivery status. |
| **Manager** | Full control over the menu, user groups, and all orders. |

Permissions are implemented in `permissions.py`:

- `IsManagerOrReadOnly`: safe methods are open to everyone; writes require the Manager group.
- `IsManager`: Manager group only.
- `IsDeliveryCrew`: Delivery crew group only.

## API Reference

All endpoints below are defined in `urls.py`. Prepend whatever prefix your project's root URL configuration uses (for example `/api/`).

### Menu Items

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `menu-items` | Public | List menu items (paginated) |
| POST | `menu-items` | Manager | Create a menu item |
| GET | `menu-items/<id>` | Public | Retrieve a single menu item |
| PUT / PATCH | `menu-items/<id>` | Manager | Update a menu item |
| DELETE | `menu-items/<id>` | Manager | Delete a menu item |

### User Group Management

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `groups/manager/users` | Manager | List all managers |
| POST | `groups/manager/users` | Manager | Add a user to Managers. Body: `{"username": "<name>"}` |
| DELETE | `groups/manager/users/<id>` | Manager | Remove a user from Managers |
| GET | `groups/delivery-crew/users` | Manager | List all delivery crew |
| POST | `groups/delivery-crew/users` | Manager | Add a user to Delivery crew. Body: `{"username": "<name>"}` |
| DELETE | `groups/delivery-crew/users/<id>` | Manager | Remove a user from Delivery crew |

### Cart

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `cart/menu-items` | Authenticated | View your cart |
| POST | `cart/menu-items` | Authenticated | Add an item. Body: `{"menuitem": <id>, "quantity": <int>}`. Adding an item already in the cart increases its quantity |
| DELETE | `cart/menu-items` | Authenticated | Empty your cart |

### Orders

| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| GET | `orders` | Authenticated | List orders. Managers see all, delivery crew see their assigned orders, customers see their own |
| POST | `orders` | Authenticated | Place an order from the current cart; the cart is cleared afterward |
| GET | `orders/<id>` | Owner / assigned crew / Manager | View the items in an order |
| PUT / PATCH | `orders/<id>` | Manager / Delivery crew | Managers can set `delivery_crew` and `status`; delivery crew can only update `status` |
| DELETE | `orders/<id>` | Manager | Delete an order |

**Example: promote a user to Delivery crew**

```http
POST /groups/delivery-crew/users
Authorization: Token <manager-token>
Content-Type: application/json

{ "username": "sam" }
```

**Example: assign a delivery crew member and mark an order as delivered**

```http
PATCH /orders/12
Authorization: Token <manager-token>
Content-Type: application/json

{ "delivery_crew": 5, "status": true }
```

## Filtering, Searching, Ordering & Pagination

### Menu items (`GET menu-items`)

| Parameter | Example | Effect |
|-----------|---------|--------|
| `category` | `?category=desserts` | Case-insensitive match on category title |
| `search` | `?search=pasta` | Title contains the search text |
| `ordering` | `?ordering=-price,title` | Comma-separated fields; prefix with `-` for descending |
| `page` | `?page=2` | Page number |
| `perpage` | `?perpage=10` | Items per page (default 2, max 100) |

### Orders (`GET orders`)

| Parameter | Example | Effect |
|-----------|---------|--------|
| `status` | `?status=1` | `1` returns delivered orders; any other value returns undelivered |
| `ordering` | `?ordering=-date` | Comma-separated fields |
| `page` | `?page=2` | Page number (2 orders per page) |

## Data Models

```
Category      slug, title
MenuItem      title, price, featured, category -> Category
Cart          user -> User, menuitems -> MenuItem, quantity, unit_price, price
Order         user -> User, delivery_crew -> User (nullable), status, total, date
OrderItem     order -> Order, menuitem -> MenuItem, quantity, unit_price, price
```

Design notes:

- A category cannot be deleted while menu items reference it (`on_delete=PROTECT`).
- `Cart` enforces one row per user and menu item, and `OrderItem` enforces one row per order and menu item.
- `Order.status` is a boolean: `False` means not yet delivered, `True` means delivered.

## Project Structure

```
.
├── models.py          # Category, MenuItem, Cart, Order, OrderItem
├── serializers.py     # DRF serializers for each model
├── permissions.py     # IsManagerOrReadOnly, IsManager, IsDeliveryCrew
├── views.py           # Class-based and function-based API views
└── urls.py            # Route definitions
```

> Note: `views.py` imports from `.serializer`, so make sure the filename and the import match in your project (`serializer.py` vs `serializers.py`).

## Known Notes

A few things worth checking before deploying:

- **Cart field name mismatch.** The `Cart` model defines the relation as `menuitems`, but `views.py` filters and creates with `menuitem`. Rename one so they match, then re-run migrations.
- **Order date.** `Order.date` is a `DateTimeField(auto_now_add=True)`, so the explicit `date=date.today()` in the order creation view is redundant and can be removed.
- **Unvalidated writes on orders.** The `status` value from the request body is saved as-is, so consider validating it as a boolean.
- **Group lookups.** The group endpoints assume the "Manager" and "Delivery crew" groups already exist; a missing group will raise an error.

## License

MIT
