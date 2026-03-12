"""
CANDIDATE TASK – Add your new tests here.

Context:
  ShopEasy is a simple e-commerce app running locally at http://localhost:5050
  The app has: a product listing page, product detail pages, a cart, checkout,
  and a confirmation page.

Your tasks:
  1. Write tests for the 3 scenarios described in the README (Scenarios A, B, C).
  2. Refactor the flawed test below (see the comment).
  3. Leave a short comment at the bottom of this file explaining what else you
     would test if you had more time.

You may use the existing tests in test_product_listing.py as reference for how
fixtures and the driver work.
"""
import pytest

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# -----------------------------------------------------------------------
# TASK 2: Refactor this test. It works, but has quality problems.
#         Fix it without changing what is being tested.
# -----------------------------------------------------------------------
@pytest.mark.ui
def test_add_to_cart_bad(driver, app_server):
    driver.get(app_server)
    add_to_cart_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'add-to-cart-btn'))
    )
    add_to_cart_button.click()
    WebDriverWait(driver, 10).until(EC.title_contains('Cart'))
    assert 'Cart' in driver.title


# -----------------------------------------------------------------------
# TASK 1: Write your 3 new test cases below
# -----------------------------------------------------------------------

# Scenario A: Product detail page
# When a user clicks on a product name, they should land on the product detail page.
# The detail page should show the product name, price, and stock status.
@pytest.mark.ui
def test_product_detail_page(driver, app_server):
    driver.get(app_server)
    product_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'product-name'))
    )
    expected_name = product_link.text
    expected_price = driver.find_element(By.CLASS_NAME, 'product-price').text
    expected_stock = driver.find_element(By.CLASS_NAME, 'product-stock').text

    product_link.click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'product-detail'))
    )
    assert driver.find_element(By.CLASS_NAME, 'product-name').text == expected_name
    assert driver.find_element(By.CLASS_NAME, 'product-price').text == expected_price
    assert driver.find_element(By.CLASS_NAME, 'product-stock').text.startswith(expected_stock)


# Scenario B: Cart total calculation
# When a user adds multiple products to the cart, the displayed total
# should equal the sum of each product's price.
@pytest.mark.ui
def test_cart_total_calculation(driver, app_server):
    driver.get(app_server)
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card'))
    )

    product_cards = driver.find_elements(By.CLASS_NAME, 'product-card')
    in_stock_cards = [
        card for card in product_cards
        if 'Out of Stock' not in card.find_element(By.CLASS_NAME, 'product-stock').text
    ]

    selected_products = [
        {
            'id': card.get_attribute('data-product-id'),
            'price': float(card.find_element(By.CLASS_NAME, 'product-price').text.replace('$', '')),
        }
        for card in in_stock_cards[:2]
    ]
    expected_total = sum(product['price'] for product in selected_products)

    for index, product in enumerate(selected_products):
        current_card = driver.find_element(
            By.CSS_SELECTOR, f'.product-card[data-product-id="{product["id"]}"]'
        )
        current_card.find_element(By.CLASS_NAME, 'add-to-cart-btn').click()
        WebDriverWait(driver, 10).until(EC.title_contains('Cart'))
        if index < len(selected_products) - 1:
            driver.get(app_server)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'product-card'))
            )

    cart_total = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'cart-total'))
    ).text
    assert cart_total == f'Total: ${expected_total:.2f}'


# Scenario C: Checkout form validation
# When a user submits the checkout form with missing required fields,
# an error message should be displayed and the order should NOT be confirmed.
@pytest.mark.ui
def test_checkout_form_validation(driver, app_server):
    driver.get(app_server)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, 'add-to-cart-btn'))
    ).click()

    WebDriverWait(driver, 10).until(EC.title_contains('Cart'))
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'checkout-btn'))
    ).click()

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'checkout-form'))
    )
    driver.find_element(By.ID, 'place-order-btn').click()

    error_message = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'error-message'))
    )
    assert error_message.text == 'All fields are required.'
    assert '/checkout' in driver.current_url
    assert '/order-confirmed' not in driver.current_url


# -----------------------------------------------------------------------
# TASK 3: Leave your note here
# -----------------------------------------------------------------------
# What else would you test if you had more time?
# (A few bullet points is all we need.)
# - Negative ad edge cases, not only happy path
# - POM for easier maintenance test cases in the future
# - test cases for cart and products tabs like quantity updates, item removal, and total recalculation after changes
# - e2e purchase flow
