# Testing

This document outlines how I test Fabric Focus to ensure the project functions as intended, the user experience is consistent across devices and browsers, and core flows (browsing products and account sign-in/sign-out) behave predictably.

The testing approach follows a combination of **Behaviour-Driven Development (BDD)** and **Test-Driven Development (TDD)** principles:

- **BDD (Behaviour-Driven Development):** Focused on real-world user stories, such as *“As a visitor, I want to view the products list so I can browse what’s available.”*
- **TDD (Test-Driven Development):** Where automated tests exist (or are added), tests are written first to encourage correct, maintainable code. (Current state: `products/tests.py` contains a regression test for sorting; `home/tests.py`, `bag/tests.py`, and `checkout/tests.py` are still placeholders.)

Both **manual** and **automated** testing methods may be used to validate the functionality, usability, and accessibility of the application.

## Table of Contents

- [Testing](#testing)
- [Table of Contents](#table-of-contents)
- [Stripe testing](#stripe-testing)
- [Account email verification testing](#account-email-verification-testing)
- [Stripe webhook command-output evidence](#stripe-webhook-command-output-evidence)
- [Testing scope and notes](#testing-scope-and-notes)
- [Responsiveness Testing](#responsiveness-testing)
- [HTML Validator Testing](#html-validator-testing)
- [CSS Validator Testing](#css-validator-testing)
- [Lighthouse Testing](#lighthouse-testing)
- [User Stories](#user-stories)
- [1. Browse Products](#1-browse-products)
- [2. View Product Details](#2-view-product-details)
- [3. Create Account / Login / Logout](#3-create-account--login--logout)
- [4. Search Products](#4-search-products)
- [5. Responsive Navigation + Header Spacing](#5-responsive-navigation--header-spacing)
- [6. Product Images and Fallbacks](#6-product-images-and-fallbacks)
- [7. Admin / Product Management (Superuser)](#7-admin--product-management-superuser)
- [Bug Tracker](#bug-tracker)
- [Testing Table](#testing-table)

## Stripe testing

- Mock `stripe.PaymentIntent.create` in unit tests; do not call the real Stripe API during unit testing.
- For integration tests, provide a test `STRIPE_SECRET_KEY` in the test environment (never commit real or live keys).
- Developer secrets for local runs can be placed in `env.py` (this repo ignores `env.py`).

### Test card numbers

Use these card numbers in test mode. Enter any future expiry date, any CVC, and any postal code.

| Card number         | Scenario                                | How to test                                                                                                   |
| ------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| 4242424242424242    | Payment succeeds (no authentication)    | Fill in the credit card form with this number and any expiry, CVC, and postal code.                           |
| 4000002500003155    | Payment requires authentication (3DS)   | Fill in the credit card form with this number and complete the authentication when prompted.                  |
| 4000000000009995    | Card declined (e.g. insufficient_funds) | Fill in the credit card form with this number and any expiry, CVC, and postal code.                           |
| 6205500000000000004 | UnionPay (variable length 13–19 digits) | Fill in the credit card form with this number (adjust length if needed) and any expiry, CVC, and postal code. |

## Account email verification testing

- Local development uses Django's console email backend (`django.core.mail.backends.console.EmailBackend`).
- Verification emails are printed to the terminal running `manage.py runserver`; no real inbox delivery occurs in local testing.
- Test accounts can use placeholder addresses (for example `tester@example.com`) because the verification URL is copied from terminal output.
- Verification is completed by opening the printed `/accounts/confirm-email/<key>/` link in the browser.

## Stripe webhook command-output evidence

Date run: 2026-02-25

### Environment checks

```powershell
stripe version
```

Observed output:

```text
stripe version 1.37.0
Checking for new versions...
```

```powershell
python manage.py check
```

Observed output:

```text
System check identified no issues (0 silenced).
```

### Webhook endpoint check

```powershell
python manage.py shell -c "from django.test import Client; c=Client(); r=c.post('/checkout/wh/', data='{}', content_type='application/json', HTTP_HOST='localhost'); print('status=', r.status_code)"
```

Observed output:

```text
status= 400
Bad Request: /checkout/wh/
```

Note: This 400 is expected for an unsigned test request. Stripe signature verification requires a valid `Stripe-Signature` header and payload.

### Handler method checks

```powershell
python manage.py shell -c "from django.test import RequestFactory; from checkout.webhook_handler import StripeWH_Handler; req=RequestFactory().post('/checkout/wh/'); h=StripeWH_Handler(req); events=['payment_intent.created','payment_intent.succeeded','payment_intent.payment_failed']; [print(et, '->', (h.handle_event({'type':et}) if et=='payment_intent.created' else h.handle_payment_intent_succeeded({'type':et}) if et=='payment_intent.succeeded' else h.handle_payment_intent_payment_failed({'type':et})).status_code) for et in events]"
```

Observed output:

```text
payment_intent.created -> 200
payment_intent.succeeded -> 200
payment_intent.payment_failed -> 200
```

This confirms the webhook handler class methods for unhandled, succeeded, and failed payment-intent events all return HTTP 200 responses.

### Webhook reconciliation evidence

Date run: 2026-02-26

- Added order traceability fields: `original_bag` and `stripe_pid`.
- Updated checkout submit flow to persist `stripe_pid` (from client secret) and `original_bag` with the order.
- Updated webhook success handler to:
  - Retry order lookup up to 5 times with a 1-second delay.
  - Match on customer/address/total plus `original_bag` and `stripe_pid`.
  - Create the order only if no match is found.

Observed dedupe validation output:

```text
pi=pi_... call1_delta=1 call2_delta=0
Webhook received: payment_intent.succeeded | SUCCESS: created order in webhook
Webhook received: payment_intent.succeeded | VERIFIED order already in database
```

## Testing scope and notes

Key areas covered in testing include:
- Navigation and URL routing (home, products, and accounts routes)
- Product listing template rendering (name/price/rating, and image handling)
- Authentication flows (sign up, login, logout) via Django Allauth
- Django admin checks for product/category management (models are registered in the admin)
- Cross-browser and mobile responsiveness (Bootstrap layout)

Current implementation notes (as of this version of the repo):
- The Products app includes a list view, product detail view, and a basic search flow via the `q` query string (e.g. `/products/?q=soft`).
- The products template references a placeholder image (`MEDIA_URL + noimage.png`) when a product has no image; the fallback file exists at `media/noimage.png`.

For each user story, **black box testing** is applied — evaluating the system purely from the user’s perspective without needing knowledge of internal code logic.

All discovered bugs, fixes, and retests should be documented throughout this file.

For additional project details and technical information, including instructions on running the site, please refer to the [README.md](./README.md)


## Responsiveness Testing

Fabric Focus uses Bootstrap (via CDN in the base template) and I manually check common Bootstrap breakpoints to ensure a consistent experience.

Breakpoints I test:

- **320px:** smallest mobile
- **576px:** mobile
- **768px:** tablet portrait
- **992px:** tablet landscape / laptop
- **1200px:** desktop

| 320px | 576px | 768px | 992px | 1200px |
| :---: | :---: | :---: | :---: | :----: |
| Passed | Passed | Passed | Passed | Passed |

Screenshot locations I use (I can create these folders to store evidence in the repo):

- `testing-images/responsiveness/320/`
- `testing-images/responsiveness/576/`
- `testing-images/responsiveness/768/`
- `testing-images/responsiveness/992/`
- `testing-images/responsiveness/1200/`

**Manual test steps:**

1. Start the Django dev server.
2. Open the site in Chrome / Edge / Firefox.
3. Open DevTools (F12) → Toggle device toolbar.
4. Set the viewport to each breakpoint above.
5. Verify:
	- Header and navigation remain usable
	- Product list cards/rows don’t overflow
	- Text remains readable and buttons/links are tappable
6. Capture screenshots and save them into the folders above.

----

## HTML Validator Testing

HTML validation helps ensure templates render valid markup across browsers and improves maintainability.

Tool:
- W3C HTML Validator: https://validator.w3.org/

**Pages to validate (examples):**

- Home page (`/`)
- Products list (`/products/`)
- Authentication pages under `/accounts/` (login / signup)

**How to run HTML validation:**

1. Open the page in your browser.
2. Right-click → “View Page Source” (or copy rendered HTML from DevTools).
3. Paste the HTML into the validator (or validate by URL if my site is accessible).
4. Record errors/warnings and retest after fixes.

**Results:**

- Home page: Passed
- Products list: Passed
- Accounts pages: Passed

----

## CSS Validator Testing

CSS validation helps catch syntax issues and improves cross-browser reliability.

Tool:
- W3C CSS Validator: https://jigsaw.w3.org/css-validator/

**What to validate:**

- First-party stylesheet(s), e.g. `static/css/base.css`

Notes (how I interpret results):

- Bootstrap is a third-party dependency loaded via CDN; I record third-party warnings separately and don’t usually treat them as defects in my own code.

**How to run CSS validation:**

1. Submit the CSS file URL (if publicly accessible) or paste the CSS into the validator.
2. Record any errors and fix them in the project CSS.
3. Re-run validation and capture evidence screenshots.

**Results:**

- `static/css/base.css`: Passed

----

## Lighthouse Testing

Lighthouse (Chrome DevTools) audits pages for performance, accessibility, best practices, and SEO.

**How to run Lighthouse:**

1. Open Chrome DevTools (F12).
2. Go to the “Lighthouse” tab.
3. Run audits on key pages (at minimum: `/` and `/products/`).
4. Record scores and any key recommendations.

**Results (I record scores here):**

| Page         | Performance | Accessibility | Best Practices |   SEO |
| ------------ | ----------: | ------------: | -------------: | ----: |
| `/`          | Passed      | Passed        | Passed         | Passed |
| `/products/` | Passed      | Passed        | Passed         | Passed |

Notes:

- Scores can vary between runs (network conditions, cold cache, background processes).
- For consistency, I run audits in an Incognito window with extensions disabled.

---

## User Stories

### 1. Browse Products

- [x] Tested

**Story:**
As a visitor, I want to view the products list so that I can browse what’s available.

**Acceptance criteria:**

- Given I navigate to `/products/`
- When the page loads
- Then I can see a list/grid of products
- And each product shows at least a name and price

**Manual test steps:**

1. Navigate to `/products/`.
2. Confirm the page loads without server errors.
3. Confirm product cards/rows render and do not overlap.
4. If products have ratings/images, confirm they display correctly.

**Bug tracking / notes:**

- See the Bug Tracker section at the bottom of this document.

---

### 2. View Product Details

- [x] Tested

**Story:**
As a visitor, I want to click a product and view its details so that I can learn more before purchasing.

**Acceptance criteria:**

- Given I am on the products list
- When I click a product
- Then I am taken to a product detail page
- And I can see the product’s name, description, price, and image (if available)

**Manual test steps:**

1. Navigate to `/products/`.
2. Click a product image/name.
3. Confirm the page loads without server errors.
4. Confirm the page shows the product name, description, and price.
5. If the product has an image, confirm it renders; if not, confirm a placeholder image is shown.

**Bug tracking / notes:**

- See the Bug Tracker section at the bottom of this document.

---

### 3. Create Account / Login / Logout

- [x] Tested

**Story:**
As a visitor, I want to create an account and log in so that I can access account-only features.

**Acceptance criteria:**

- Given I visit `/accounts/signup/`
- When I submit a valid registration form
- Then an account is created (and I’m either signed in or prompted to verify/sign in)

- Given I have an account
- When I sign in at `/accounts/login/`
- Then I can log out successfully

**Manual test steps:**

1. Go to `/accounts/signup/` and complete the form with valid details.
2. Confirm the app accepts the registration.
3. Go to `/accounts/login/` and sign in.
4. Confirm the header shows the logged-in state (e.g. “Logout” option).
5. Log out and confirm I’m returned to a logged-out state.

**Bug tracking / notes:**

- See the Bug Tracker section at the bottom of this document.

---

### 4. Search Products

- [x] Tested

**Story:**
As a visitor, I want to search for products so that I can quickly find items by name or description.

**Acceptance criteria:**

- Given I am on any page with the search box
- When I submit a search term (e.g. `soft`)
- Then I am taken to `/products/?q=soft`
- And the results list is filtered to matching products

- Given I submit an empty search
- When I press search
- Then I receive a helpful error message
- And I am redirected back to the products page

**Manual test steps:**

1. Use the header search input and submit `soft`.
2. Confirm the URL becomes `/products/?q=soft`.
3. Confirm the page loads without server errors and shows results.
4. Submit an empty search and confirm a message is shown and the app returns to `/products/`.

**Bug tracking / notes:**

- See Bug #3 for a previous server error found during search testing.

---

### 5. Responsive Navigation + Header Spacing

- [x] Tested

**Story:**
As a mobile visitor, I want the navigation/header to work without overlapping page content so that I can browse and search comfortably.

**Acceptance criteria:**

- Given I’m on a mobile-width screen (below 992px)
- When the navbar collapses
- Then page content (including the products header) starts below the navbar
- And the search form remains usable

**Manual test steps:**

1. Open the site on a mobile device (or use Chrome responsive mode).
2. Navigate to `/products/`.
3. Confirm the Products header/content isn’t hidden under the navbar.
4. Open the navbar toggler and confirm it expands/collapses cleanly.

**Bug tracking / notes:**

- See Bug #2 for a mobile header spacing issue and fix.

---

### 6. Product Images and Fallbacks

- [x] Tested

**Story:**
As a visitor, I want products to show an image (or a sensible placeholder) so that the product grid looks consistent.

**Acceptance criteria:**

- Given a product has an uploaded image
- When I view `/products/`
- Then the product card shows that image

- Given a product does not have an uploaded image
- When I view `/products/`
- Then a placeholder image is displayed instead of a broken image

**Manual test steps:**

1. On `/products/`, find one product with an image and confirm it loads.
2. Find one product without an image and confirm the placeholder image loads.
3. Click through to the product detail page and repeat the same checks.

**Bug tracking / notes:**

- If placeholder images 404, I log it in the Bug Tracker with the missing file path.

---

### 7. Admin / Product Management (Superuser)

- [x] Tested

**Story:**
As an admin user, I want to manage products through the Django admin so that I can add and update items.

**Acceptance criteria:**

- Given I am logged in as a superuser
- When I visit `/admin/`
- Then I can create, edit, and delete products and categories

**Manual test steps:**

1. Log in as a superuser.
2. Navigate to `/admin/`.
3. Create a test product (or edit an existing one) and save.
4. Confirm the change is visible on `/products/`.

**Bug tracking / notes:**

- Any admin form errors or missing fields get logged in the Bug Tracker.

---

## Bug Tracker

I log bugs here as I find them during manual testing and validation.

How I use this table:

- **ID:** incremental number
- **Area/Feature:** where the issue occurs (page, flow, component)
- **Description:** what happened + what I expected
- **Steps to Reproduce:** clear steps from a fresh page load
- **Status:** Open / In Progress / Fixed / Retest Needed
- **Fix Summary:** short note on what I changed (file/symbol if useful)

| ID  | Area / Feature                                         | Description                                                                                                                                                                                                                                                    | Steps to Reproduce                                                                                                                                                                                                                                                        | Status | Fix Summary                                                                                                                                                                                                                                                                                                                                                   |
| --- | ------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Products routing (`/products/`) + product detail links | Dev server failed to start due to a syntax error in the Products URLconf, and the products views were incomplete. Expected: `runserver` starts and `/products/` loads; clicking a product navigates to its detail page.                                        | 1) In the project root, run `python manage.py runserver` (or `python manage.py check`).<br>2) Before the fix, Django raises a `SyntaxError` in `products/urls.py` (“Perhaps you forgot a comma?”).<br>3) After the fix, visit `/products/` and click a product card link. | Fixed  | Fixed `products/urls.py` by adding the missing comma and using `path('<int:product_id>/', ...)`. Updated `products/views.py` so `all_products` returns `products/products.html` and `product_detail(request, product_id)` renders `products/product_detail.html`. Retested locally on 2026-02-03 (dev server starts; `/products/` loads; product links work). |
| 2   | Mobile header spacing (Products page)                  | On mobile widths, the header/content on the main Products page wasn’t pushed down far enough when the navbar collapses, so content sat underneath the nav. Expected: the content starts below the collapsed navbar.                                            | 1) Open `/products/` on a mobile device (or devtools responsive mode).<br>2) Ensure the navbar is in its collapsed state (below 992px wide).<br>3) Observe the header/content position under the navbar.                                                                  | Fixed  | Added a mobile media query in `static/css/base.css` (`@media (max-width: 991px)`) to set `.header-container { padding-top: 116px; }` and adjusted `body` height to `calc(100vh - 116px)`. Retest on a real device on 2026-02-03.                                                                                                                              |
| 3   | Products search (`/products/?q=...`)                   | Searching from the header caused a server error: `NameError` in `all_products` because the search filter used invalid `Q()` syntax (e.g. `name_icontains-query`) instead of proper ORM lookups. Expected: `/products/?q=soft` returns a filtered product list. | 1) Go to `/products/`.<br>2) Use the search box and submit `soft` (or visit `/products/?q=soft`).<br>3) Before the fix, Django raises `NameError: name 'name_icontains' is not defined` in `products/views.py`. | Fixed  | Updated `products/views.py` to use `Q(name__icontains=query) \| Q(description__icontains=query)` and apply `.distinct()` to the filtered queryset. Retested locally on 2026-02-04 (search query executes and returns results). |
| 4   | Products sorting (sort by name)                        | Sorting by name caused a server error: `NameError at /products/` → `name 'Lower' is not defined` in `all_products`. Expected: sorting by name works and returns the products list.                                                                             | 1) Visit `/products/?sort=name&direction=asc`.<br>2) Before the fix, Django raises `NameError: name 'Lower' is not defined` in `products/views.py` (during `products.annotate(lower_name=Lower('name'))`).                                                                | Fixed  | Imported `Lower` from `django.db.models.functions` in `products/views.py`. Added regression test in `products/tests.py` to ensure `/products/?sort=name&direction=asc` returns 200. Retested on 2026-02-09.                                                                                                                                                   |
| 5   | Dev server startup + Bag routing (`/bag/`)             | Dev server would not start after adding the Bag app: Django failed during URL configuration load with `AttributeError: module 'bag.views' has no attribute 'index'`. Expected: `runserver` starts and `/bag/` loads.                                           | 1) Add `path('bag/', include('bag.urls'))` to the project URLconf.<br>2) Run `python manage.py runserver` (or `python manage.py check`).<br>3) Before the fix, Django errors because `bag/urls.py` referenced `views.index` but the view is named `view_bag`.             | Fixed  | Updated `bag/urls.py` to use `views.view_bag`. Also fixed a broken template URL tag in `templates/base.html` so the desktop bag icon links to `{% url 'view_bag' %}`. Retested locally on 2026-02-10 (`manage.py check` passes; server starts; `/bag/` returns 200).                                                                                          |
| 6   | Shopping bag item size display (`/bag/`)               | On the bag page, item size display could show incorrect/misleading output instead of the selected size value for each line item. Expected: bag line items show `Size: XS/S/M/L/XL` when a size exists, otherwise `N/A`.                                        | 1) Add a product with size to bag from product detail page.<br>2) Visit `/bag/`.<br>3) Check the line item metadata under product name and verify the size label output.                                                                                                  | Fixed  | Updated `bag/templates/bag/bag.html` to render size from `item.size` directly with fallback. Also aligned bag data handling in `bag/contexts.py` and `bag/views.py` so sized items carry correct quantity/size context. Retested on 2026-02-18.                                                                                                               |
| 7   | Shopping bag remove action (`/bag/`)                   | Clicking Remove did not consistently remove items during bag testing. Expected: Remove deletes the selected line item and refreshes the bag page.                                                                                                              | 1) Add one or more products to bag.<br>2) Visit `/bag/`.<br>3) Click Remove on a line item.<br>4) Before fix, item may persist or fail to remove depending on request mismatch.                                                                                           | Fixed  | Updated remove-link JS in `bag/templates/bag/bag.html` to post to `/bag/remove/<item_id>/` with consistent `product_size` payload naming and added failure handling. Retested on 2026-02-18.                                                                                                                                                                  |
| 8   | Bag JavaScript dependency/protocol (`base.html`)       | Bag AJAX actions can fail when jQuery is loaded incorrectly (slim build or insecure/incorrect protocol). Expected: full jQuery over HTTPS is loaded so `$.post` works reliably.                                                                                | 1) Open `/bag/` and try Remove/Update actions.<br>2) If jQuery is slim or loaded incorrectly, JS behaviors may fail and AJAX methods may be unavailable.<br>3) Check browser console/network for script-load/AJAX errors.                                                 | Fixed  | Confirmed full jQuery (non-slim) is loaded via HTTPS in `templates/base.html`, which supports AJAX methods used by bag scripts. Retested on 2026-02-18.                                                                                                                                                                                                       |
| 9   | Shopping bag subtotal calculation (`/bag/`)            | Subtotal column was not using a dedicated template calculation pattern. Expected: each row subtotal equals quantity × unit price.                                                                                                                              | 1) Add items to bag and vary quantity.<br>2) Visit `/bag/` and inspect row subtotal values.<br>3) Confirm subtotal updates with quantity and price.                                                                                                                       | Fixed  | Added custom template filter `calc_subtotal` in `bag/templatetags/bag_tools.py`, added `bag/templatetags/__init__.py`, loaded it in `bag/templates/bag/bag.html`, and updated subtotal render to use `item.product.price` with the `calc_subtotal` filter. Retested on 2026-02-18.                                                                            |

| 10  | Media context processor (`settings.py`)                 | Product images with no image file failed to load placeholder image due to missing media context processor. Expected: `{% MEDIA_URL %}` works in templates and placeholder image loads.                                  | 1) Visit product page or checkout with product missing image.<br>2) Before fix, placeholder image fails to load.<br>3) After fix, add `'django.template.context_processors.media'` to settings.py.<br>4) Placeholder image loads correctly. | Fixed  | Added `'django.template.context_processors.media'` to context processors in settings.py. Verified placeholder image loads in templates.                                                                                                                                    |

| 11  | Checkout template parsing (`/checkout/`)               | Checkout page errored with `TemplateSyntaxError` (`Invalid block tag ... expected 'endif'`) due to a malformed split `{% endif %}` inside the order-summary loop. Expected: checkout page renders normally.           | 1) Visit `/checkout/`.<br>2) Before fix, Django raises template parsing error around the size line in `checkout.html`.<br>3) After fix, page loads and order summary displays with size fallback.                                                                 | Fixed  | Corrected malformed if/else/endif markup in `checkout/templates/checkout/checkout.html` so `{% endif %}` is valid and in-line. Retested on 2026-02-26 by loading template and checkout page.                                                                                   |
| 12  | Success template parsing (`/checkout/checkout_success/`) | Success page errored with `TemplateSyntaxError` (`Invalid block tag ... expected 'elif', 'else' or 'endif'`) due to a malformed split `{% endif %}` in line-item rendering. Expected: success page renders fully. | 1) Complete checkout and open `/checkout/checkout_success/<order_number>`.<br>2) Before fix, page fails to render with template error near line-item block.<br>3) After fix, order details render correctly.                                                         | Fixed  | Corrected malformed if/endif markup in `checkout/templates/checkout/checkout_success.html` for the `item.product_size` conditional. Retested on 2026-02-26 by loading template and success page.                                                                              |
| 13  | Stripe country code mapping (`/checkout/`)             | Payment confirmation failed when checkout country text was sent to Stripe (e.g., `United Kingdom`), which expects ISO-3166-1 alpha-2 values (e.g., `GB`). Expected: checkout country is normalized before Stripe call. | 1) Start checkout with country shown as `United Kingdom`.<br>2) Before fix, payment can fail with `Country 'United Kingdom' is unknown`.<br>3) After fix, country is converted to `GB` and payment request is accepted.                                               | Fixed  | Updated `checkout/static/checkout/js/stripe_elements.js` to normalize country aliases (e.g., `UK`, `United Kingdom`) to ISO code `GB` before `stripe.confirmCardPayment`. Retested on 2026-02-26.                                                                              |
| 14  | Duplicate postcode capture in checkout (`/checkout/`)  | Stripe card UI requested postcode/ZIP in addition to the existing delivery postcode field. Expected: only one postcode input in checkout flow.                                                                 | 1) Open `/checkout/`.<br>2) Before fix, Stripe card element shows an extra ZIP/postcode field.<br>3) After fix, Stripe card field is hidden and checkout postcode is reused in payment data.                                                                        | Fixed  | Updated `checkout/static/checkout/js/stripe_elements.js` to set `hidePostalCode: true` and reuse `form.postcode` for billing/shipping `postal_code`. Retested on 2026-02-26.                                                                                                  |
| 15  | Success billing formatting (`/checkout/checkout_success/`) | Billing totals on success page displayed without a currency symbol/consistent formatting. Expected: UK currency format with `£` and 2 decimal places for order, delivery, and grand total.                       | 1) Complete an order and view success page billing section.<br>2) Before fix, totals appear as plain decimals.<br>3) After fix, values display as `£xx.xx`.                                                                                                        | Fixed  | Updated `checkout/templates/checkout/checkout_success.html` to render `order_total`, `delivery_cost`, and `grand_total` as `£{{ value|floatformat:2 }}`. Retested on 2026-02-26.                                                                                             |
| 16  | Webhook/order race condition (`/checkout/wh/`)          | `payment_intent.succeeded` can arrive before checkout view finishes saving, risking duplicate or missing orders. Expected: webhook waits and verifies order before creating.                                                                                   | 1) Complete checkout while webhook is active.<br>2) Before fix, async timing can create inconsistent outcomes.<br>3) After fix, webhook retries lookup (5x, 1s) before fallback creation.                                                                          | Fixed  | Added retry loop in `checkout/webhook_handler.py` so webhook attempts to find order multiple times before creating it. Retested on 2026-02-26.                                                                                                                              |
| 17  | Webhook order identity matching (`/checkout/wh/`)       | Matching on customer/address/total alone can be ambiguous for repeat purchases. Expected: identify an order by the exact checkout payload + Stripe PaymentIntent ID.                                                                                        | 1) Process payments with similar customer/address values.<br>2) Before fix, matching can be ambiguous.<br>3) After fix, lookup includes `original_bag` and `stripe_pid`.                                                                                           | Fixed  | Added `Order.original_bag` and `Order.stripe_pid` fields (migration `0002_auto_20260226_0822`) and included them in checkout save + webhook lookup/create paths. Retested on 2026-02-26.                                                                                   |
| 18  | Webhook fallback create path (`/checkout/wh/`)          | If checkout form submission fails after payment confirmation, order can be missing in DB. Expected: webhook creates order from PaymentIntent metadata as fallback.                                                                                           | 1) Simulate missing form submit after payment confirmation.<br>2) Before fix, paid order may not exist in DB.<br>3) After fix, webhook creates order and returns success response.                                                                                   | Fixed  | Implemented webhook fallback creation from metadata bag and shipping/billing details in `checkout/webhook_handler.py`. Retested on 2026-02-26.                                                                                                                            |
| 19  | Success toast on profile page (`/profile/`)             | Success toast could render checkout bag summary content when viewing profile, which is unrelated and noisy on that page. Expected: profile page toasts should not include bag-summary section.                                                               | 1) Navigate to `/profile/` and trigger a success message.<br>2) Before fix, toast may include bag/total summary section when `grand_total` is present.<br>3) After fix, bag-summary section is hidden on profile page.                                              | Fixed  | Updated `templates/includes/toasts/toast_success.html` to gate bag-summary render with `not on_profile_page`, and set `on_profile_page` in `profiles/views.py` context. Retested on 2026-03-03.                                                                            |

## Testing Table

This table summarises key test cases and their results for core project features.

| Test Case                          | Area / Feature | Steps / Description                 | Expected Result              | Actual Result | Status |
| ---------------------------------- | -------------- | ----------------------------------- | ---------------------------- | ------------- | ------ |
| Homepage loads                     | Home page      | Visit `/`                           | Page loads, no errors        | As expected   | Passed |
| Product list loads                 | Products       | Visit `/products/`                  | Product list visible         | As expected   | Passed |
| Product detail loads               | Products       | Click product from list             | Detail page visible          | As expected   | Passed |
| Add to bag                         | Bag            | Add product to bag                  | Bag updates                  | As expected   | Passed |
| Remove from bag                    | Bag            | Remove product from bag             | Bag updates                  | As expected   | Passed |
| Checkout form renders              | Checkout       | Visit `/checkout/`                  | Form visible                 | As expected   | Passed |
| User registration                  | Accounts       | Register new user                   | Account created              | As expected   | Passed |
| Login/logout                       | Accounts       | Login and logout flows              | Auth works                   | As expected   | Passed |
| Admin access                       | Admin          | Login as superuser, visit `/admin/` | Admin dashboard loads        | As expected   | Passed |
| Invalid login                      | Accounts       | Attempt login with wrong password   | Error message shown          | As expected   | Passed |
| Password reset                     | Accounts       | Request password reset email        | Email sent, can reset        | As expected   | Passed |
| Search products                    | Products       | Use search box with query           | Filtered results shown       | As expected   | Passed |
| Empty search                       | Products       | Submit empty search                 | Error message, redirect      | As expected   | Passed |
| Add product with size              | Bag            | Add product with size to bag        | Size shown in bag            | As expected   | Passed |
| Remove product with size           | Bag            | Remove sized product from bag       | Bag updates                  | As expected   | Passed |
| Responsive layout (mobile)         | Layout         | View site on mobile device          | Layout adapts, no overlap    | As expected   | Passed |
| Responsive layout (desktop)        | Layout         | View site on desktop                | Layout adapts, no overlap    | As expected   | Passed |
| Placeholder image for no product   | Products       | View product with no image          | Placeholder image shown      | As expected   | Passed |
| Add-to-bag toast notification      | Bag            | Add item to bag                     | Toast notification appears   | As expected   | Passed |
| Remove-from-bag toast notification | Bag            | Remove item from bag                | Toast notification appears   | As expected   | Passed |
| Admin create product               | Admin          | Create product in admin             | Product appears in list      | As expected   | Passed |
| Admin edit product                 | Admin          | Edit product in admin               | Changes visible in list      | As expected   | Passed |
| Admin delete product               | Admin          | Delete product in admin             | Product removed from list    | As expected   | Passed |
| Checkout with empty bag            | Checkout       | Try to checkout with empty bag      | Error message, redirect      | As expected   | Passed |
| Checkout with filled bag           | Checkout       | Checkout with items in bag          | Order form shown             | As expected   | Passed |
| Webhook dedupe on same PI          | Checkout/Stripe | Call `payment_intent.succeeded` twice for same PaymentIntent | First call creates order; second verifies existing | As expected   | Passed |
| Webhook fallback order creation    | Checkout/Stripe | Simulate payment confirmed without final form submit | Webhook creates order from metadata | As expected   | Passed |
| CSS validation                     | Static files   | Validate base.css                   | No errors/warnings           | As expected   | Passed |
| HTML validation                    | Templates      | Validate home/products templates    | No errors/warnings           | As expected   | Passed |
| Lighthouse audit                   | Site           | Run Lighthouse on home/products     | Good scores, no major issues | As expected   | Passed |





