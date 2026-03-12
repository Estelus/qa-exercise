"""
BONUS TASK (optional) – API Tests

If you have time remaining after the UI tasks, add 2–3 API test cases here.

Endpoints available:
  GET    /api/products          – list all products
  GET    /api/products/<id>     – single product or 404
  GET    /api/cart              – current cart: {cart, items, total, item_count}
  POST   /api/cart/<id>         – add product to cart; returns updated cart
  DELETE /api/cart/<id>         – remove product from cart; returns updated cart
  POST   /api/checkout          – place order {name, email, address}; 200 or 422

Ideas (pick any):
  - Verify a product response contains expected fields (id, name, price, stock, category)
  - Verify a non-existent product returns 404 with an "error" field
  - Verify adding a product updates item_count and total correctly
  - Verify checkout returns 422 when required fields are missing
  - Verify checkout clears the cart on success
"""
import pytest

pytestmark = pytest.mark.api

def test_adding_product_updates_cart_totals(api_client):
    session, base_url = api_client

    response = session.post(f"{base_url}/api/cart/1")

    assert response.status_code == 200
    payload = response.json()
    assert payload["item_count"] == 1
    assert payload["total"] == 79.99
    assert payload["cart"] == {"1": 1}
    assert payload["items"][0]["id"] == 1
    assert payload["items"][0]["quantity"] == 1
    assert payload["items"][0]["subtotal"] == 79.99

def test_get_missing_product_returns_404_with_error(api_client):
    session, base_url = api_client

    response = session.get(f"{base_url}/api/products/999")

    assert response.status_code == 404
    assert response.json() == {"error": "Product not found"}

def test_checkout_returns_422_when_required_fields_are_missing(api_client):
    session, base_url = api_client
    session.post(f"{base_url}/api/cart/1")

    response = session.post(
        f"{base_url}/api/checkout",
        json={"name": "", "email": "user@example.com", "address": ""},
    )

    assert response.status_code == 422
    assert response.json() == {"error": "All fields are required."}
