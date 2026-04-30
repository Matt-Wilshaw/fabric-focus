# Testing

Live site: https://fabric-focus-f1a8e9ed6562.herokuapp.com/

This document records the testing evidence for Fabric-Focus as an assessment submission. It is intended to demonstrate that the application has been checked for functionality, responsiveness, validation, accessibility, and the main customer journey from browsing through to checkout.

Testing in this project combines:

- manual end-to-end testing of real user flows
- automated regression testing using Django's built-in test framework, covering models, forms, views, and security controls
- validator, Lighthouse, and compatibility checks to support front-end quality evidence

This file records the full testing evidence completed during development and before submission, including automated test output, manual test results, and validation snapshots.

## Submission Summary

At submission stage:

- core customer flows have been manually tested on the deployed application
- responsive checks have been carried out across standard Bootstrap breakpoints
- HTML and CSS validation evidence has been recorded
- Lighthouse checks have been captured for key pages
- Stripe checkout and webhook behaviour have been tested in test mode
- the AI style assistant has been tested for disclaimer visibility and outfit suggestion responses
- automated Django test coverage across models, forms, views, and security controls is documented below
- order confirmation and order-history access controls were retested after an authorisation fix so users can only access their own orders
- order confirmation in the current project is on-screen and by email only; no SMS notification service is implemented

## Table of Contents

- [Testing](#testing)
  - [Submission Summary](#submission-summary)
  - [Table of Contents](#table-of-contents)
  - [Stripe Testing](#stripe-testing)
    - [Test Card Numbers](#test-card-numbers)
  - [Account Email Verification Testing](#account-email-verification-testing)
  - [Stripe Webhook Command-Output Evidence](#stripe-webhook-command-output-evidence)
    - [Environment Checks](#environment-checks)
    - [Webhook Endpoint Check](#webhook-endpoint-check)
    - [Handler Method Checks](#handler-method-checks)
    - [Webhook Reconciliation Evidence](#webhook-reconciliation-evidence)
  - [Testing Scope and Notes](#testing-scope-and-notes)
  - [Known Limitations](#known-limitations)
  - [Automated Test Execution Evidence — 2026-04-16](#automated-test-execution-evidence--2026-04-16)
  - [Automated Test Execution Evidence — 2026-04-28](#automated-test-execution-evidence--2026-04-28)
  - [Browser Compatibility Matrix](#browser-compatibility-matrix)
  - [Responsiveness Testing](#responsiveness-testing)
  - [HTML Validator Testing](#html-validator-testing)
    - [Final Validation Summary](#final-validation-summary)
    - [Validation Cleanup Summary](#validation-cleanup-summary)
    - [Homepage (`/`) Validation Snapshot](#homepage--validation-snapshot)
    - [Products List (`/products/`) Validation Snapshot](#products-list-products-validation-snapshot)
    - [Product Detail (`/products/2/`) Validation Snapshot](#product-detail-products2-validation-snapshot)
    - [Bag (`/bag/`) Validation Snapshot](#bag-bag-validation-snapshot)
    - [Checkout (`/checkout/`) Validation Snapshot](#checkout-checkout-validation-snapshot)
    - [Account Login (`/accounts/login/`) Validation Snapshot](#account-login-accountslogin-validation-snapshot)
    - [Account Signup (`/accounts/signup/`) Validation Snapshot](#account-signup-accountssignup-validation-snapshot)
  - [CSS Validator Testing](#css-validator-testing)
    - [CSS Validation Summary by Page](#css-validation-summary-by-page)
  - [Accessibility Testing](#accessibility-testing)
    - [Screen Reader Evidence Log](#screen-reader-evidence-log)
    - [Keyboard-Only Result (Representative)](#keyboard-only-result-representative)
    - [Contrast Evidence Log](#contrast-evidence-log)
    - [Known Accessibility Issues](#known-accessibility-issues)
  - [Lighthouse Testing](#lighthouse-testing)
    - [Homepage (`/`) Previous Mobile Lighthouse Evidence](#homepage--previous-mobile-lighthouse-evidence)
    - [Homepage (`/`) Final Mobile Lighthouse Evidence](#homepage--final-mobile-lighthouse-evidence)
  - [User Stories](#user-stories)
    - [1. Browse Products](#1-browse-products)
    - [2. View Product Details](#2-view-product-details)
    - [3. Create Account / Login / Logout](#3-create-account--login--logout)
    - [4. Search Products](#4-search-products)
    - [5. Responsive Navigation + Header Spacing](#5-responsive-navigation--header-spacing)
    - [6. Product Images and Fallbacks](#6-product-images-and-fallbacks)
    - [7. Admin / Product Management (Superuser)](#7-admin--product-management-superuser)
    - [8. Add-to-Bag Redirect Stability (Regression)](#8-add-to-bag-redirect-stability-regression)
    - [9. Checkout](#9-checkout)
    - [10. Order History](#10-order-history)
    - [11. AI Style Assistant (What to Wear)](#11-ai-style-assistant-what-to-wear)
  - [Bug Tracker](#bug-tracker)
  - [Testing Table](#testing-table)

## Stripe Testing

- Mock `stripe.PaymentIntent.create` in unit tests; do not call the real Stripe API during unit testing.
- For integration tests, provide a test `STRIPE_SECRET_KEY` in the test environment (never commit real or live keys).
- Developer secrets for local runs can be placed in `env.py` (this repo ignores `env.py`).

### Test Card Numbers

Use these card numbers in test mode. Enter any future expiry date, any CVC, and any postal code.

| Card number         | Scenario                                | How to test                                                                                                   |
| ------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| 4242424242424242    | Payment succeeds (no authentication)    | Fill in the credit card form with this number and any expiry, CVC, and postal code.                           |
| 4000002500003155    | Payment requires authentication (3DS)   | Fill in the credit card form with this number and complete the authentication when prompted.                  |
| 4000000000009995    | Card declined (e.g. insufficient_funds) | Fill in the credit card form with this number and any expiry, CVC, and postal code.                           |
| 6205500000000000004 | UnionPay (variable length 13–19 digits) | Fill in the credit card form with this number (adjust length if needed) and any expiry, CVC, and postal code. |

## Account Email Verification Testing

- Local development uses Django's console email backend (`django.core.mail.backends.console.EmailBackend`).
- Verification emails are printed to the terminal running `manage.py runserver`; no real inbox delivery occurs in local testing.
- Test accounts can use placeholder addresses (for example `tester@example.com`) because the verification URL is copied from terminal output.
- Verification is completed by opening the printed `/accounts/confirm-email/<key>/` link in the browser.

## Stripe Webhook Command-Output Evidence

Date run: 2026-02-25

### Environment Checks

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

### Webhook Endpoint Check

```powershell
python manage.py shell -c "from django.test import Client; c=Client(); r=c.post('/checkout/wh/', data='{}', content_type='application/json', HTTP_HOST='localhost'); print('status=', r.status_code)"
```

Observed output:

```text
status= 400
Bad Request: /checkout/wh/
```

Note: This 400 is expected for an unsigned test request. Stripe signature verification requires a valid `Stripe-Signature` header and payload.

### Handler Method Checks

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

### Webhook Reconciliation Evidence

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

Observed profile-integration validation output (webhook parity with checkout view):

```text
resp1= 200 Webhook received: payment_intent.succeeded | SUCCESS: Created order in webhook
resp2= 200 Webhook received: payment_intent.succeeded | SUCCESS: Verified order already in database
counts before/mid/after= 0 1 1
order_has_profile= True
saved_defaults= 07123456789 GB SW1A1AA London
```

This confirms webhook-created orders correctly attach `user_profile` and persist default delivery details when `save_info` is true.

## Testing Scope and Notes

Key areas covered in testing include:
- Navigation and URL routing (home, products, and accounts routes)
- Product listing template rendering (name/price/rating, and image handling)
- Authentication flows (sign up, login, logout) via Django Allauth
- Django admin checks for product/category management (models are registered in the admin)
- Cross-browser and mobile responsiveness (Bootstrap layout)

Current implementation notes (as of this version of the repo):
- The Products app includes a list view, product detail view, and a basic search flow via the `q` query string (e.g. `/products/?q=soft`).
- The products template references a placeholder image (`MEDIA_URL + noimage.png`) when a product has no image; the fallback file exists at `media/noimage.png`.
- Stock is not currently reserved at add-to-bag time; in high-concurrency scenarios, two users can checkout overlapping items before stock enforcement is applied (residual oversell risk).
- The checkout flow collects a phone number for delivery/contact details, but the project does not currently send SMS confirmations or delivery text updates.
- Automated unit and integration tests cover core flows using Django's built-in test framework, and manual regression testing provides additional coverage across the full project scope.
- Order access is now enforced server-side: `checkout_success` only permits the same checkout session or the rightful account owner, and `profile/order_history` requires login plus ownership of the requested order.

For each user story, **black box testing** is applied — evaluating the system purely from the user's perspective without needing knowledge of internal code logic.

All discovered bugs, fixes, and retests should be documented throughout this file.

For additional project details and technical information, including instructions on running the site, please refer to the [README.md](./README.md)

## Known Limitations

The following limitations are acknowledged at submission. They are documented here for transparency and are not testing failures — they represent features not yet implemented rather than bugs.

- Stock is not reserved at add-to-bag time. Two users could theoretically add the same last item and both proceed to checkout before either is blocked.
- The bag is session-based and is not saved to a user's account. Items will not carry over between devices or browser sessions.
- Product listings have no pagination. A large catalogue would become unwieldy to browse.
- There is no order status tracking after purchase. Customers can view order history but cannot see dispatch status.
- Stock levels are not managed in the admin. There is no quantity field on products, so overselling cannot be prevented at the catalogue level.
- Product images must be managed manually. There is no bulk upload or catalogue import facility.
- No SMS order confirmations are sent. The checkout collects a phone number for delivery contact purposes only.

## Automated Test Execution Evidence — 2026-04-16

**Note:** The command below uses a full path to the Python executable in my local virtual environment (``.venv``). This folder is not included in the repository and will not be available when cloning the project. Assessors should create and activate their own virtual environment using the provided ``requirements.txt``, then run tests with the generic command:

  python manage.py test

This ensures the tests are run in a clean, reproducible environment.

Command executed:

```powershell
C:/Projects/fabric-focus/.venv/Scripts/python.exe manage.py test
```

Observed output summary:

- Test database created and destroyed successfully.
- Django system check reported no issues.
- `Ran 23 tests in 3.005s`
- Final status: `OK`

Security-focused regression tests added in this run:

- guest users cannot open arbitrary `/checkout/checkout_success/<order_number>` pages without a matching checkout session
- authenticated users cannot open or claim another user's order from the checkout success route
- rightful owners can still access their own saved order confirmations
- `/profile/order_history/<order_number>` now requires login and blocks non-owners with HTTP 403

## Automated Test Execution Evidence — 2026-04-28

Observed output summary:

- Test database created and destroyed successfully.
- Django system check reported no issues.
- `Ran 32 tests in 4.886s`
- Final status: `OK`

This run confirms all automated unit and integration tests pass in the current development environment.

## Browser Compatibility Matrix

Core customer flows checked: home, products list/detail, bag actions, login/logout, and checkout page render.

| Browser / Profile            | Result                | Notes                                                                                                                                                                                                                     |
| ---------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Chrome (desktop)             | Passed                | Primary manual test browser used throughout the project.                                                                                                                                                                  |
| Edge (desktop)               | Passed                | Core navigation and form flows matched Chrome behaviour.                                                                                                                                                                  |
| Firefox (desktop)            | Passed                | No layout or interaction regressions found in core flows.                                                                                                                                                                 |
| Chrome mobile emulation      | Passed                | Used during responsiveness checks at 320/576/768/992/1200 breakpoints.                                                                                                                                                    |
| Mobile Safari (iOS hardware) | Limited retest passed | Follow-up retest on 2026-03-31 focused on homepage horizontal overflow and mobile layout behaviour after the iPhone-reported bug fix. Full end-to-end Safari regression coverage was not repeated across every user flow. |


## Responsiveness Testing

Fabric-Focus uses Bootstrap (via CDN in the base template), and responsiveness was tested manually across common Bootstrap breakpoints to ensure a consistent experience.

Breakpoints I test:

- **320px:** smallest mobile
- **576px:** mobile
- **768px:** tablet portrait
- **992px:** tablet landscape / laptop
- **1200px:** desktop

| 320px  | 576px  | 768px  | 992px  | 1200px |
| :----: | :----: | :----: | :----: | :----: |
| Passed | Passed | Passed | Passed | Passed |

Responsiveness screenshot evidence captured from the built application:

**320px**

Homepage  
![320px homepage responsiveness](testing-images/responsiveness/320/homepage.png)

Products  
![320px products responsiveness](testing-images/responsiveness/320/products.png)

Checkout  
![320px checkout responsiveness](testing-images/responsiveness/320/checkout.png)

**576px**

Homepage  
![576px homepage responsiveness](testing-images/responsiveness/576/homepage.png)

Products  
![576px products responsiveness](testing-images/responsiveness/576/products.png)

Checkout  
![576px checkout responsiveness](testing-images/responsiveness/576/checkout.png)

**768px**

Homepage  
![768px homepage responsiveness](testing-images/responsiveness/768/homepage.png)

Products  
![768px products responsiveness](testing-images/responsiveness/768/products.png)

Checkout  
![768px checkout responsiveness](testing-images/responsiveness/768/checkout.png)

**992px**

Homepage  
![992px homepage responsiveness](testing-images/responsiveness/992/homepage.png)

Products  
![992px products responsiveness](testing-images/responsiveness/992/products.png)

Checkout  
![992px checkout responsiveness](testing-images/responsiveness/992/checkout.png)

**1200px**

Homepage  
![1200px homepage responsiveness](testing-images/responsiveness/1200/homepage.png)

Products  
![1200px products responsiveness](testing-images/responsiveness/1200/products.png)

Checkout  
![1200px checkout responsiveness](testing-images/responsiveness/1200/checkout.png)


**Manual test steps:**

1. Start the Django dev server.
2. Open the site in Chrome / Edge / Firefox.
3. Open DevTools (F12) → Toggle device toolbar.
4. Set the viewport to each breakpoint above.
5. Verify:
  - Header and navigation remain usable
  - Product list cards/rows don't overflow
  - Text remains readable and buttons/links are tappable
6. Capture screenshots from the built application and save them in the testing evidence folder before linking them in this document.

---

## HTML Validator Testing

HTML validation was carried out using the [W3C Markup Validation Service](https://validator.w3.org/).

### Final Validation Summary

Final validation rerun date: 2026-03-24

The deployed Heroku site was revalidated after the shared-template cleanup and final heading/link fixes. All tested pages now return zero HTML validation messages.

Key fixes included:

- removing invalid dropdown `aria-labelledby` usage from shared header/navigation templates
- renaming the mobile account dropdown trigger so IDs remain unique
- replacing product-management subheadings with paragraph text
- correcting the style-assistant heading order
- removing the trailing slash from the shared Font Awesome stylesheet tag

Verification:

- `manage.py check` passed after the changes
- the deployed site was checked via the W3C validator JSON API after deployment

| Page                | Full validator result                                                                                                        | Errors | Warnings | Info |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------- | ------ | -------- | ---- |
| `/`                 | [View result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2F)                     | 0      | 0        | 0    |
| `/products/`        | [View result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Fproducts%2F)          | 0      | 0        | 0    |
| `/products/2/`      | [View result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Fproducts%2F2%2F)      | 0      | 0        | 0    |
| `/bag/`             | [View result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Fbag%2F)               | 0      | 0        | 0    |
| `/checkout/`        | [View result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Fcheckout%2F)          | 0      | 0        | 0    |
| `/accounts/login/`  | [View result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Faccounts%2Flogin%2F)  | 0      | 0        | 0    |
| `/accounts/signup/` | [View result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Faccounts%2Fsignup%2F) | 0      | 0        | 0    |

Historical validator output from before the cleanup is retained below for traceability.

### Validation Cleanup Summary

Initial validator runs highlighted a set of repeated shared-template issues rather than isolated page-specific failures. The main problems were:

- Dropdown menu containers using `aria-labelledby` on generic `<div>` elements in shared navigation partials.
- Heading hierarchy skips in product-management templates.
- Historical navbar-semantic findings that needed to be rechecked after shared-template cleanup.

Fixes applied on 2026-03-24:

- Removed invalid `aria-labelledby` usage from Bootstrap dropdown menu containers in the shared header/navigation templates.
- Replaced product-management subheadings from `<h5>` to muted paragraph text so heading order remains consistent.
- Kept the earlier validator tables below as a historical snapshot of the issue state before cleanup.

Retest status:

- `manage.py check` passes after the cleanup.
- A post-deploy W3C validator JSON API rerun was captured on 2026-03-24 and confirmed zero errors, zero warnings, and zero info messages across the tested pages.

### Homepage (`/`) Validation Snapshot

**Page tested:** `https://fabric-focus-f1a8e9ed6562.herokuapp.com/`

🔗 [View full validation result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2F)

| #   | Type      | Description                                                                                                                                                                                                                                                          | Location     |
| --- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1   | ℹ️ Info    | Trailing slash on void elements has no effect and interacts badly with unquoted attribute values.                                                                                                                                                                    | Line 44–45   |
| 2   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 98      |
| 3   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 127     |
| 4   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 135     |
| 5   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 151     |
| 6   | ❌ Error   | Duplicate ID "user-options".                                                                                                                                                                                                                                         | Line 152–153 |
| 7   | ⚠️ Warning | The first occurrence of ID "user-options" was here.                                                                                                                                                                                                                  | Line 91–92   |
| 8   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 159     |
| 9   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 166     |
| 10  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 187     |
| 11  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 201     |
| 12  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 218     |
| 13  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 324     |
| 14  | ❌ Error   | The heading "h4" (with computed level 4) follows the heading "h2" (with computed level 2), skipping 1 heading level.                                                                                                                                                 | Line 232     |
| 15  | ❌ Error   | The heading "h4" (with computed level 4) follows the heading "h1" (with computed level 1), skipping 2 heading levels.                                                                                                                                                | Line 256     |

**Summary:** 12 errors · 2 warnings · 1 info notice

### Products List (`/products/`) Validation Snapshot

**Page Tested:** `https://fabric-focus-f1a8e9ed6562.herokuapp.com/products/`

🔗 [View full validation result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Fproducts%2F)

| #   | Type      | Description                                                                                                                                                                                                                                                          | Location     |
| --- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1   | ℹ️ Info    | Trailing slash on void elements has no effect and interacts badly with unquoted attribute values.                                                                                                                                                                    | Line 44–45   |
| 2   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 98      |
| 3   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 127     |
| 4   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 135     |
| 5   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 151     |
| 6   | ❌ Error   | Duplicate ID "user-options".                                                                                                                                                                                                                                         | Line 152–153 |
| 7   | ⚠️ Warning | The first occurrence of ID "user-options" was here.                                                                                                                                                                                                                  | Line 91–92   |
| 8   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 159     |
| 9   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 166     |
| 10  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 187     |
| 11  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 201     |
| 12  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 218     |
| 13  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 5937    |
| 14  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 6089    |
| 15  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 6095    |
| 16  | ❌ Error   | The heading "h4" (with computed level 4) follows the heading "h2" (with computed level 2), skipping 1 heading level.                                                                                                                                                 | Line 232     |

**Summary:** 11 errors · 4 warnings · 1 info notice

### Product Detail (`/products/2/`) Validation Snapshot

**Page Tested:** `https://fabric-focus-f1a8e9ed6562.herokuapp.com/products/2/`

🔗 [View full validation result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Fproducts%2F2%2F)

| #   | Type      | Description                                                                                                                                                                                                                                                          | Location     |
| --- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1   | ℹ️ Info    | Trailing slash on void elements has no effect and interacts badly with unquoted attribute values.                                                                                                                                                                    | Line 44–45   |
| 2   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 98      |
| 3   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 127     |
| 4   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 135     |
| 5   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 151     |
| 6   | ❌ Error   | Duplicate ID "user-options".                                                                                                                                                                                                                                         | Line 152–153 |
| 7   | ⚠️ Warning | The first occurrence of ID "user-options" was here.                                                                                                                                                                                                                  | Line 91–92   |
| 8   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 159     |
| 9   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 166     |
| 10  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 187     |
| 11  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 201     |
| 12  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 218     |
| 13  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 397     |
| 14  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 549     |
| 15  | ❌ Error   | The heading "h4" (with computed level 4) follows the heading "h2" (with computed level 2), skipping 1 heading level.                                                                                                                                                 | Line 232     |

**Summary:** 11 errors · 3 warnings · 1 info notice

### Bag (`/bag/`) Validation Snapshot

**Page Tested:** `https://fabric-focus-f1a8e9ed6562.herokuapp.com/bag/`

🔗 [View full validation result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Fbag%2F)

| #   | Type      | Description                                                                                                                                                                                                                                                          | Location     |
| --- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1   | ℹ️ Info    | Trailing slash on void elements has no effect and interacts badly with unquoted attribute values.                                                                                                                                                                    | Line 44–45   |
| 2   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 98      |
| 3   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 127     |
| 4   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 135     |
| 5   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 151     |
| 6   | ❌ Error   | Duplicate ID "user-options".                                                                                                                                                                                                                                         | Line 152–153 |
| 7   | ⚠️ Warning | The first occurrence of ID "user-options" was here.                                                                                                                                                                                                                  | Line 91–92   |
| 8   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 159     |
| 9   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 166     |
| 10  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 187     |
| 11  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 201     |
| 12  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 218     |
| 13  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 335     |
| 14  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 487     |
| 15  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 531     |
| 16  | ❌ Error   | The heading "h4" (with computed level 4) follows the heading "h2" (with computed level 2), skipping 1 heading level.                                                                                                                                                 | Line 232     |

**Summary:** 11 errors · 4 warnings · 1 info notice

### Checkout (`/checkout/`) Validation Snapshot

**Page Tested:** `https://fabric-focus-f1a8e9ed6562.herokuapp.com/checkout/`

🔗 [View full validation result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Fcheckout%2F)

| #   | Type      | Description                                                                                                                                                                                                                                                          | Location     |
| --- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1   | ℹ️ Info    | Trailing slash on void elements has no effect and interacts badly with unquoted attribute values.                                                                                                                                                                    | Line 44–45   |
| 2   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 98      |
| 3   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 127     |
| 4   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 135     |
| 5   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 151     |
| 6   | ❌ Error   | Duplicate ID "user-options".                                                                                                                                                                                                                                         | Line 152–153 |
| 7   | ⚠️ Warning | The first occurrence of ID "user-options" was here.                                                                                                                                                                                                                  | Line 91–92   |
| 8   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 159     |
| 9   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 166     |
| 10  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 187     |
| 11  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 201     |
| 12  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 218     |
| 13  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 5959    |
| 14  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 6111    |
| 15  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 6117    |
| 16  | ❌ Error   | The heading "h4" (with computed level 4) follows the heading "h2" (with computed level 2), skipping 1 heading level.                                                                                                                                                 | Line 232     |

**Summary:** 11 errors · 4 warnings · 1 info notice

### Account Login (`/accounts/login/`) Validation Snapshot

**Page Tested:** `https://fabric-focus-f1a8e9ed6562.herokuapp.com/accounts/login/`

🔗 [View full validation result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Faccounts%2Flogin%2F)

| #   | Type      | Description                                                                                                                                                                                                                                                          | Location     |
| --- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1   | ℹ️ Info    | Trailing slash on void elements has no effect and interacts badly with unquoted attribute values.                                                                                                                                                                    | Line 47–48   |
| 2   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 101     |
| 3   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 130     |
| 4   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 138     |
| 5   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 154     |
| 6   | ❌ Error   | Duplicate ID "user-options".                                                                                                                                                                                                                                         | Line 155–156 |
| 7   | ⚠️ Warning | The first occurrence of ID "user-options" was here.                                                                                                                                                                                                                  | Line 94–95   |
| 8   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 162     |
| 9   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 169     |
| 10  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 190     |
| 11  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 204     |
| 12  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 221     |
| 13  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 363     |
| 14  | ❌ Error   | The heading "h4" (with computed level 4) follows the heading "h2" (with computed level 2), skipping 1 heading level.                                                                                                                                                 | Line 235     |

**Summary:** 11 errors · 2 warnings · 1 info notice

### Account Signup (`/accounts/signup/`) Validation Snapshot

**Page Tested:** `https://fabric-focus-f1a8e9ed6562.herokuapp.com/accounts/signup/`

🔗 [View full validation result](https://validator.w3.org/nu/?doc=https%3A%2F%2Ffabric-focus-f1a8e9ed6562.herokuapp.com%2Faccounts%2Fsignup%2F)

| #   | Type      | Description                                                                                                                                                                                                                                                          | Location     |
| --- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------ |
| 1   | ℹ️ Info    | Trailing slash on void elements has no effect and interacts badly with unquoted attribute values.                                                                                                                                                                    | Line 47–48   |
| 2   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 101     |
| 3   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 130     |
| 4   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 138     |
| 5   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 154     |
| 6   | ❌ Error   | Duplicate ID "user-options".                                                                                                                                                                                                                                         | Line 155–156 |
| 7   | ⚠️ Warning | The first occurrence of ID "user-options" was here.                                                                                                                                                                                                                  | Line 94–95   |
| 8   | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 162     |
| 9   | ❌ Error   | Element "li" not allowed as child of element "nav" in this context. (Suppressing further errors from this subtree.)                                                                                                                                                  | Line 169     |
| 10  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 190     |
| 11  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 204     |
| 12  | ❌ Error   | The "aria-labelledby" attribute must not be specified on any "div" element unless the element has a "role" value other than "caption", "code", "deletion", "emphasis", "generic", "insertion", "paragraph", "presentation", "strong", "subscript", or "superscript". | Line 221     |
| 13  | ⚠️ Warning | The "type" attribute is unnecessary for JavaScript resources.                                                                                                                                                                                                        | Line 351     |
| 14  | ❌ Error   | The heading "h4" (with computed level 4) follows the heading "h2" (with computed level 2), skipping 1 heading level.                                                                                                                                                 | Line 235     |

**Summary:** 11 errors · 2 warnings · 1 info notice

---

## CSS Validator Testing

CSS validation was carried out using the [W3C CSS Validation Service](https://jigsaw.w3.org/css-validator/).

**Validator settings:** CSS Level 3 + SVG

Latest live rerun date: 2026-03-24

### CSS Validation Summary by Page

| Page                | Full validator result                                                                                                                                                                           | Errors | Warnings |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ | -------- |
| `/`                 | [View result](https://jigsaw.w3.org/css-validator/validator?uri=https://fabric-focus-f1a8e9ed6562.herokuapp.com/&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)                 | 0      | 738      |
| `/products/`        | [View result](https://jigsaw.w3.org/css-validator/validator?uri=https://fabric-focus-f1a8e9ed6562.herokuapp.com/products/&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)        | 0      | 738      |
| `/products/2/`      | [View result](https://jigsaw.w3.org/css-validator/validator?uri=https://fabric-focus-f1a8e9ed6562.herokuapp.com/products/2/&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)      | 0      | 738      |
| `/bag/`             | [View result](https://jigsaw.w3.org/css-validator/validator?uri=https://fabric-focus-f1a8e9ed6562.herokuapp.com/bag/&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)             | 0      | 738      |
| `/checkout/`        | [View result](https://jigsaw.w3.org/css-validator/validator?uri=https://fabric-focus-f1a8e9ed6562.herokuapp.com/checkout/&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)        | 0      | 738      |
| `/accounts/login/`  | [View result](https://jigsaw.w3.org/css-validator/validator?uri=https://fabric-focus-f1a8e9ed6562.herokuapp.com/accounts/login/&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en)  | 0      | 738      |
| `/accounts/signup/` | [View result](https://jigsaw.w3.org/css-validator/validator?uri=https://fabric-focus-f1a8e9ed6562.herokuapp.com/accounts/signup/&profile=css3svg&usermedium=all&warning=1&vextwarning=&lang=en) | 0      | 738      |

> Note: all tested pages reported `0` CSS errors on the live rerun. The `738` warnings are largely informational and come from CSS variables, vendor extensions, Bootstrap, and Font Awesome rather than unresolved stylesheet errors in the project CSS.

---

## Accessibility Testing

Accessibility was reviewed through manual checks, semantic validation, and Lighthouse snapshots. This section explicitly separates what is confirmed, partially audited, and not yet fully audited.

Accessibility test environment (representative run):

- Date: 2026-04-15
- OS: Windows
- Screen reader: NVDA 2025.3.3
- Browser: Google Chrome 146.0.7680.178

Confirmed checks:

- Final HTML validation reruns returned `0` errors, `0` warnings, and `0` info messages across the tested pages.
- Product imagery includes `alt` text and decorative icons use `aria-hidden` or accessible labels where appropriate.
- Key form-driven pages (`/checkout/`, `/accounts/login/`, `/accounts/signup/`, `/profile/`) were checked for visible labels, validation feedback, and submit controls.
- Core interactive components were manually checked for keyboard reachability (shared header, account menu, bag actions, checkout flow, authentication forms).
- The style assistant panel includes a visible disclaimer prompting users to double-check important details.
- Windows high-contrast checks were captured as supporting evidence (`readme-images/miscellaneous/accessibility-contrast-test.png` and `readme-images/miscellaneous/accessibility-contrast-test2.png`).

Partially audited:

- Practical contrast checks were completed on core flows.
- Lighthouse mobile snapshots were captured on key pages.
- The historical homepage CTA contrast finding was retested after a style update on 2026-04-15 and is now tracked as fixed in the Bug Tracker.

Not yet fully audited:

- A formal WCAG 2.1/2.2 AA conformance audit across all templates, states, and error paths.
- A complete screen-reader test matrix (for example NVDA/JAWS/VoiceOver) across end-to-end user journeys.
- Automated accessibility checks in CI (for example axe/pa11y) are not currently configured.

Outcome summary:

- Markup quality improved as part of the HTML validation fixes on 2026-03-24.
- Homepage Lighthouse mobile accessibility score on the final 2026-04-30 screenshot: `100`.
- Lighthouse previously flagged the mobile search and account menu icon links as missing discernible names; the mobile header controls now include explicit `aria-label` values.
- Homepage CTA contrast issue is tracked in the Bug Tracker as item `29` (Fixed).

### Screen Reader Evidence Log

Representative desktop evidence captured for this submission:

| Assistive tech | Platform/browser                | Page/flow tested                  | Evidence file path                                    | Result                  | Notes                                                                                                                                           |
| -------------- | ------------------------------- | --------------------------------- | ----------------------------------------------------- | ----------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| NVDA           | Windows + Chrome 146.0.7680.178 | Home navigation and header menus  | `readme-images/miscellaneous/nvda-screen-reader.png`  | Passed (representative) | Screenshot captured with NVDA output visible during navigation checks. This is a representative sample rather than a full screen-reader matrix. |
| NVDA           | Windows + Chrome 146.0.7680.178 | Product imagery/tag announcements | `readme-images/miscellaneous/nvda-screen-reader2.png` | Passed (representative) | Additional representative screenshot showing NVDA announcements for product imagery/tag-related content.                                        |

### Keyboard-Only Result (Representative)

- Keyboard tab navigation reached primary navigation, account controls, bag actions, and form controls in representative desktop checks.
- Visible focus indicators were present on tested interactive elements.
- No keyboard trap was observed during the representative checks.

### Contrast Evidence Log

| Check type                | Platform        | Evidence file path                                             | Result                  | Notes                                                                                |
| ------------------------- | --------------- | -------------------------------------------------------------- | ----------------------- | ------------------------------------------------------------------------------------ |
| High contrast mode review | Windows desktop | `readme-images/miscellaneous/accessibility-contrast-test.png`  | Passed (representative) | Visual proof captured during high-contrast testing of key interface elements.        |
| High contrast mode review | Windows desktop | `readme-images/miscellaneous/accessibility-contrast-test2.png` | Passed (representative) | Additional supporting screenshot captured during the same practical contrast checks. |

### Known Accessibility Issues

- Evidence in this section is representative and practical; a full WCAG conformance audit and full assistive-technology matrix are still pending.

---

## Lighthouse Testing

Lighthouse (Chrome DevTools) audits pages for performance, accessibility, best practices, and SEO.

Latest captured audit: 2026-04-30

Test profile used:

- Device profile: mobile
- Browser: Chrome DevTools Lighthouse 13.0.2
- Run mode: navigation
- Test environment: mobile emulation with Lighthouse's default throttling profile

**How to run Lighthouse:**

1. Open Chrome DevTools (F12).
2. Go to the "Lighthouse" tab.
3. Run audits on key pages (at minimum: `/` and `/products/`).
4. Record scores and any key recommendations.

**Results:**

| Page | Date       | Performance | Accessibility | Best Practices | SEO |
| ---- | ---------- | ----------- | ------------- | -------------- | --- |
| `/`  | 2026-03-24 | 57          | 94            | 100            | 91  |
| `/`  | 2026-04-30 | 77          | 100           | 100            | 100 |

Notes:

- Scores can vary between runs (network conditions, cold cache, background processes).
- For consistency, I run audits in an Incognito window with extensions disabled.
- The 2026-03-24 row records the previous captured homepage mobile Lighthouse run.
- The 2026-04-30 row records the final homepage mobile Lighthouse run after image/performance work and mobile header accessibility labels.

### Homepage (`/`) Previous Mobile Lighthouse Evidence

Report metadata:

- URL tested: `https://fabric-focus-f1a8e9ed6562.herokuapp.com/`
- Lighthouse version: `13.0.2`
- Fetch time: `2026-03-24`
- Form factor: mobile
- Browser profile: Chrome mobile emulation

Summary scores captured for `/` on 2026-03-24:

- Performance: `57`
- Accessibility: `94`
- Best Practices: `100`
- SEO: `91`

Key findings:

- Performance: this earlier homepage run reported a lower performance score than the later 2026-04-30 rerun.
- Accessibility: score of `94` indicates at least one remaining accessibility opportunity was present in the earlier homepage audit.
- SEO: score of `91` indicates a minor SEO opportunity was present in the earlier homepage audit.
- Best Practices: `100` — no issues flagged.

### Homepage (`/`) Final Mobile Lighthouse Evidence

Report metadata:

- URL tested: `https://fabric-focus-f1a8e9ed6562.herokuapp.com/`
- Lighthouse version: `13.0.2`
- Fetch time: `2026-04-30`
- Form factor: mobile
- Browser profile: Chrome mobile emulation

Summary scores captured for `/` on 2026-04-30:

- Performance: `77`
- Accessibility: `100`
- Best Practices: `100`
- SEO: `100`

Evidence screenshot:

- `testing-images/lighthouse/lighthouse-testing-final.png`

Supporting evidence from the same report:

- First Contentful Paint: `4.1 s`
- Largest Contentful Paint: `4.1 s`
- Speed Index: `4.1 s`
- Total Blocking Time: `60 ms`
- Cumulative Layout Shift: `0`

Key findings called out by Lighthouse:

- Accessibility: final screenshot shows the homepage mobile accessibility score increased to `100` after the mobile search, account menu, search submit, and bag controls were given explicit accessible names.
- Performance: score improved from the previous captured homepage score of `57` to `77`.
- Performance note: the improvement is likely helped by the smaller homepage hero image and the later Python/Django upgrade, alongside normal Lighthouse run-to-run variation.
- Performance: render-blocking requests were identified as the largest optimisation opportunity, with estimated savings of `2,970 ms`.
- Performance: cache lifetime, font display, document request latency, unused JavaScript, unused CSS, and CSS minification were also identified as optimisation opportunities.

---

## User Stories

### 1. Browse Products

- [x] Tested

**Story:**
As a visitor, I want to view the products list so that I can browse what's available.

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
- And I can see the product's name, description, price, and image (if available)

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
- Then an account is created (and I'm either signed in or prompted to verify/sign in)

- Given I have an account
- When I sign in at `/accounts/login/`
- Then I can log out successfully

**Manual test steps:**

1. Go to `/accounts/signup/` and complete the form with valid details.
2. Confirm the app accepts the registration.
3. Go to `/accounts/login/` and sign in.
4. Confirm the header shows the logged-in state (e.g. "Logout" option).
5. Log out and confirm I'm returned to a logged-out state.

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

- Given I'm on a mobile-width screen (below 992px)
- When the navbar collapses
- Then page content (including the products header) starts below the navbar
- And the search form remains usable

**Manual test steps:**

1. Open the site on a mobile device (or use Chrome responsive mode).
2. Navigate to `/products/`.
3. Confirm the Products header/content isn't hidden under the navbar.
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

### 8. Add-to-Bag Redirect Stability (Regression)

- [x] Tested

**Story:**
As a shopper, I want product detail pages to remain stable after adding an item to the bag so that I can continue browsing without server errors.

**Acceptance criteria:**

- Given I am on a product detail page (for example `/products/2/`)
- When I submit Add to Bag
- Then the POST to `/bag/add/<id>/` returns a redirect (`302`)
- And the redirected product detail page returns `200` (no `500`)

**Manual test steps:**

1. Open `/products/<id>/`.
2. Choose a size when applicable and submit Add to Bag.
3. Confirm `/bag/add/<id>/` returns `302`.
4. Confirm the next GET to `/products/<id>/` returns `200`.
5. Repeat for multiple products to reduce false confidence from a single-item check.

**Regression evidence (2026-03-19):**

- Root cause: malformed template block structure in `templates/includes/toasts/toast_success.html`.
- Symptom pattern: issue triggered after successful Add to Bag because success-message toast rendering hit a template parsing error.
- Fix: corrected the conditional tag structure in the success toast template.
- Verification:
  - Production flow validated across product IDs `1-12`.
  - For all sampled IDs: `GET /products/<id>/ = 200`, `POST /bag/add/<id>/ = 302`, redirected `GET /products/<id>/ = 200`.
  - Recent Heroku log window showed no new `status=500` or `TemplateSyntaxError` entries during retest.

---

### 9. Checkout

- [x] Tested

**Story:**
As a shopper, I want to complete a purchase securely so that I can buy products with confidence.

**Acceptance criteria:**

- Given I have items in my bag
- When I proceed to checkout and submit valid delivery and payment details
- Then my order is confirmed on-screen and by email
- And a Stripe payment intent is created and confirmed

**Manual test steps:**

1. Add one or more items to the bag.
2. Navigate to `/checkout/`.
3. Complete the delivery form with valid details.
4. Enter Stripe test card `4242424242424242` with any future expiry, CVC, and postal code.
5. Submit the form and confirm the order confirmation page loads.
6. Confirm a confirmation email is sent to the provided address.

**Bug tracking / notes:**

- See Bug Tracker for previous checkout template and webhook issues.

---

### 10. Order History

- [x] Tested

**Story:**
As a registered user, I want to view my past orders so that I can keep track of my purchases.

**Acceptance criteria:**

- Given I am logged in
- When I visit my profile
- Then I can see a list of my past orders
- And I can click through to view the full details of each order

**Manual test steps:**

1. Log in as a registered user who has placed at least one order.
2. Navigate to `/profile/`.
3. Confirm past orders are listed.
4. Click an order and confirm the order detail page loads with correct information.
5. Confirm that attempting to view another user's order is blocked.

**Bug tracking / notes:**

- See Bug #32 for the order authorisation fix.

---

### 11. AI Style Assistant (What to Wear)

- [x] Tested

**Story:**
As a shopper, I want to use the style assistant to get outfit suggestions based on occasion or preference so that I can find products suited to my needs.

**Acceptance criteria:**

- Given I am on a products page
- When I click the "What to wear" button
- Then the assistant panel opens
- And I can select a preset option or type my own prompt
- And the assistant returns an outfit suggestion
- And a disclaimer is visible before I submit

**Manual test steps:**

1. Navigate to `/products/` or a product detail page.
2. Click the "What to wear" button and confirm the panel opens.
3. Select a preset option (e.g. "Casual weekend") and confirm a suggestion is returned.
4. Type a custom prompt and submit, confirm a suggestion is returned.
5. Inspect the disclaimer text above the input and confirm it is clearly visible before submitting.

**Bug tracking / notes:**

- The assistant is intentionally shown only on product browsing pages where outfit guidance is most relevant.
- If the `GEMINI_API_KEY` is missing, the widget falls back to keyword-based responses.

---

## Bug Tracker

I log bugs here as I find them during automated, manual testing and validation.

How I use this table:

- **ID:** incremental number
- **Area/Feature:** where the issue occurs (page, flow, component)
- **Description:** what happened + what I expected
- **Steps to Reproduce:** clear steps from a fresh page load
- **Status:** Open / In Progress / Fixed / Retest Needed
- **Fix Summary:** short note on what I changed (file/symbol if useful)
- 
| ID  | Area / Feature                                                                                                                      | Description                                                                                                                                                                                                                                                                                                        | Steps to Reproduce                                                                                                                                                                                                                                                                                                            | Status             | Fix Summary                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| --- | ----------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Products routing (`/products/`) + product detail links                                                                              | Dev server failed to start due to a syntax error in the Products URLconf, and the products views were incomplete. Expected: `runserver` starts and `/products/` loads; clicking a product navigates to its detail page.                                                                                            | 1) In the project root, run `python manage.py runserver` (or `python manage.py check`).<br>2) Before the fix, Django raises a `SyntaxError` in `products/urls.py` ("Perhaps you forgot a comma?").<br>3) After the fix, visit `/products/` and click a product card link.                                                     | Fixed              | Fixed `products/urls.py` by adding the missing comma and using `path('<int:product_id>/', ...)`. Updated `products/views.py` so `all_products` returns `products/products.html` and `product_detail(request, product_id)` renders `products/product_detail.html`. Retested locally on 2026-02-03 (dev server starts; `/products/` loads; product links work).                                                                                        |
| 2   | Mobile header spacing (Products page)                                                                                               | On mobile widths, the header/content on the main Products page wasn't pushed down far enough when the navbar collapses, so content sat underneath the nav. Expected: the content starts below the collapsed navbar.                                                                                                | 1) Open `/products/` on a mobile device (or devtools responsive mode).<br>2) Ensure the navbar is in its collapsed state (below 992px wide).<br>3) Observe the header/content position under the navbar.                                                                                                                      | Fixed              | Added a mobile media query in `static/css/base.css` (`@media (max-width: 991px)`) to set `.header-container { padding-top: 116px; }` and adjusted `body` height to `calc(100vh - 116px)`. Retest on a real device on 2026-02-03.                                                                                                                                                                                                                     |
| 3   | Products search (`/products/?q=...`)                                                                                                | Searching from the header caused a server error: `NameError` in `all_products` because the search filter used invalid `Q()` syntax (e.g. `name_icontains-query`) instead of proper ORM lookups. Expected: `/products/?q=soft` returns a filtered product list.                                                     | 1) Go to `/products/`.<br>2) Use the search box and submit `soft` (or visit `/products/?q=soft`).<br>3) Before the fix, Django raises `NameError: name 'name_icontains' is not defined` in `products/views.py`.                                                                                                               | Fixed              | Updated `products/views.py` to use `Q(name__icontains=query) \| Q(description__icontains=query)` and apply `.distinct()` to the filtered queryset. Retested locally on 2026-02-04 (search query executes and returns results).                                                                                                                                                                                                                       |
| 4   | Products sorting (sort by name)                                                                                                     | Sorting by name caused a server error: `NameError at /products/` → `name 'Lower' is not defined` in `all_products`. Expected: sorting by name works and returns the products list.                                                                                                                                 | 1) Visit `/products/?sort=name&direction=asc`.<br>2) Before the fix, Django raises `NameError: name 'Lower' is not defined` in `products/views.py` (during `products.annotate(lower_name=Lower('name'))`).                                                                                                                    | Fixed              | Imported `Lower` from `django.db.models.functions` in `products/views.py`. Added regression test in `products/tests.py` to ensure `/products/?sort=name&direction=asc` returns 200. Retested on 2026-02-09.                                                                                                                                                                                                                                          |
| 5   | Dev server startup + Bag routing (`/bag/`)                                                                                          | Dev server would not start after adding the Bag app: Django failed during URL configuration load with `AttributeError: module 'bag.views' has no attribute 'index'`. Expected: `runserver` starts and `/bag/` loads.                                                                                               | 1) Add `path('bag/', include('bag.urls'))` to the project URLconf.<br>2) Run `python manage.py runserver` (or `python manage.py check`).<br>3) Before the fix, Django errors because `bag/urls.py` referenced `views.index` but the view is named `view_bag`.                                                                 | Fixed              | Updated `bag/urls.py` to use `views.view_bag`. Also fixed a broken template URL tag in `templates/base.html` so the desktop bag icon links to `{% url 'view_bag' %}`. Retested locally on 2026-02-10 (`manage.py check` passes; server starts; `/bag/` returns 200).                                                                                                                                                                                 |
| 6   | Shopping bag item size display (`/bag/`)                                                                                            | On the bag page, item size display could show incorrect/misleading output instead of the selected size value for each line item. Expected: bag line items show `Size: XS/S/M/L/XL` when a size exists, otherwise `N/A`.                                                                                            | 1) Add a product with size to bag from product detail page.<br>2) Visit `/bag/`.<br>3) Check the line item metadata under product name and verify the size label output.                                                                                                                                                      | Fixed              | Updated `bag/templates/bag/bag.html` to render size from `item.size` directly with fallback. Also aligned bag data handling in `bag/contexts.py` and `bag/views.py` so sized items carry correct quantity/size context. Retested on 2026-02-18.                                                                                                                                                                                                      |
| 7   | Shopping bag remove action (`/bag/`)                                                                                                | Clicking Remove did not consistently remove items during bag testing. Expected: Remove deletes the selected line item and refreshes the bag page.                                                                                                                                                                  | 1) Add one or more products to bag.<br>2) Visit `/bag/`.<br>3) Click Remove on a line item.<br>4) Before fix, item may persist or fail to remove depending on request mismatch.                                                                                                                                               | Fixed              | Updated remove-link JS in `bag/templates/bag/bag.html` to post to `/bag/remove/<item_id>/` with consistent `product_size` payload naming and added failure handling. Retested on 2026-02-18.                                                                                                                                                                                                                                                         |
| 8   | Bag JavaScript dependency/protocol (`base.html`)                                                                                    | Bag AJAX actions can fail when jQuery is loaded incorrectly (slim build or insecure/incorrect protocol). Expected: full jQuery over HTTPS is loaded so `$.post` works reliably.                                                                                                                                    | 1) Open `/bag/` and try Remove/Update actions.<br>2) If jQuery is slim or loaded incorrectly, JS behaviours may fail and AJAX methods may be unavailable.<br>3) Check browser console/network for script-load/AJAX errors.                                                                                                    | Fixed              | Confirmed full jQuery (non-slim) is loaded via HTTPS in `templates/base.html`, which supports AJAX methods used by bag scripts. Retested on 2026-02-18.                                                                                                                                                                                                                                                                                              |
| 9   | Shopping bag subtotal calculation (`/bag/`)                                                                                         | Subtotal column was not using a dedicated template calculation pattern. Expected: each row subtotal equals quantity × unit price.                                                                                                                                                                                  | 1) Add items to bag and vary quantity.<br>2) Visit `/bag/` and inspect row subtotal values.<br>3) Confirm subtotal updates with quantity and price.                                                                                                                                                                           | Fixed              | Added custom template filter `calc_subtotal` in `bag/templatetags/bag_tools.py`, added `bag/templatetags/__init__.py`, loaded it in `bag/templates/bag/bag.html`, and updated subtotal render to use `item.product.price` with the `calc_subtotal` filter. Retested on 2026-02-18.                                                                                                                                                                   |
| 10  | Media context processor (`settings.py`)                                                                                             | Product images with no image file failed to load placeholder image due to missing media context processor. Expected: `{% MEDIA_URL %}` works in templates and placeholder image loads.                                                                                                                             | 1) Visit product page or checkout with product missing image.<br>2) Before fix, placeholder image fails to load.<br>3) After fix, add `'django.template.context_processors.media'` to settings.py.<br>4) Placeholder image loads correctly.                                                                                   | Fixed              | Added `'django.template.context_processors.media'` to context processors in settings.py. Verified placeholder image loads in templates.                                                                                                                                                                                                                                                                                                              |
| 11  | Checkout template parsing (`/checkout/`)                                                                                            | Checkout page errored with `TemplateSyntaxError` (`Invalid block tag ... expected 'endif'`) due to a malformed split `{% endif %}` inside the order-summary loop. Expected: checkout page renders normally.                                                                                                        | 1) Visit `/checkout/`.<br>2) Before fix, Django raises template parsing error around the size line in `checkout.html`.<br>3) After fix, page loads and order summary displays with size fallback.                                                                                                                             | Fixed              | Corrected malformed if/else/endif markup in `checkout/templates/checkout/checkout.html` so `{% endif %}` is valid and in-line. Retested on 2026-02-26 by loading template and checkout page.                                                                                                                                                                                                                                                         |
| 12  | Success template parsing (`/checkout/checkout_success/`)                                                                            | Success page errored with `TemplateSyntaxError` (`Invalid block tag ... expected 'elif', 'else' or 'endif'`) due to a malformed split `{% endif %}` in line-item rendering. Expected: success page renders fully.                                                                                                  | 1) Complete checkout and open `/checkout/checkout_success/<order_number>`.<br>2) Before fix, page fails to render with template error near line-item block.<br>3) After fix, order details render correctly.                                                                                                                  | Fixed              | Corrected malformed if/endif markup in `checkout/templates/checkout/checkout_success.html` for the `item.product_size` conditional. Retested on 2026-02-26 by loading template and success page.                                                                                                                                                                                                                                                     |
| 13  | Stripe country code mapping (`/checkout/`)                                                                                          | Payment confirmation failed when checkout country text was sent to Stripe (e.g., `United Kingdom`), which expects ISO-3166-1 alpha-2 values (e.g., `GB`). Expected: checkout country is normalized before Stripe call.                                                                                             | 1) Start checkout with country shown as `United Kingdom`.<br>2) Before fix, payment can fail with `Country 'United Kingdom' is unknown`.<br>3) After fix, country is converted to `GB` and payment request is accepted.                                                                                                       | Fixed              | Updated `checkout/static/checkout/js/stripe_elements.js` to normalize country aliases (e.g., `UK`, `United Kingdom`) to ISO code `GB` before `stripe.confirmCardPayment`. Retested on 2026-02-26.                                                                                                                                                                                                                                                    |
| 14  | Duplicate postcode capture in checkout (`/checkout/`)                                                                               | Stripe card UI requested postcode/ZIP in addition to the existing delivery postcode field. Expected: only one postcode input in checkout flow.                                                                                                                                                                     | 1) Open `/checkout/`.<br>2) Before fix, Stripe card element shows an extra ZIP/postcode field.<br>3) After fix, Stripe card field is hidden and checkout postcode is reused in payment data.                                                                                                                                  | Fixed              | Updated `checkout/static/checkout/js/stripe_elements.js` to set `hidePostalCode: true` and reuse `form.postcode` for billing/shipping `postal_code`. Retested on 2026-02-26.                                                                                                                                                                                                                                                                         |
| 15  | Success billing formatting (`/checkout/checkout_success/`)                                                                          | Billing totals on success page displayed without a currency symbol/consistent formatting. Expected: UK currency format with `£` and 2 decimal places for order, delivery, and grand total.                                                                                                                         | 1) Complete an order and view success page billing section.<br>2) Before fix, totals appear as plain decimals.<br>3) After fix, values display as `£xx.xx`.                                                                                                                                                                   | Fixed              | Updated `checkout/templates/checkout/checkout_success.html` to render `order_total`, `delivery_cost`, and `grand_total` as `£{{ value\|floatformat:2 }}`. Retested on 2026-02-26.                                                                                                                                                                                                                                                                    |
| 16  | Webhook/order race condition (`/checkout/wh/`)                                                                                      | `payment_intent.succeeded` can arrive before checkout view finishes saving, risking duplicate or missing orders. Expected: webhook waits and verifies order before creating.                                                                                                                                       | 1) Complete checkout while webhook is active.<br>2) Before fix, async timing can create inconsistent outcomes.<br>3) After fix, webhook retries lookup (5x, 1s) before fallback creation.                                                                                                                                     | Fixed              | Added retry loop in `checkout/webhook_handler.py` so webhook attempts to find order multiple times before creating it. Retested on 2026-02-26.                                                                                                                                                                                                                                                                                                       |
| 17  | Webhook order identity matching (`/checkout/wh/`)                                                                                   | Matching on customer/address/total alone can be ambiguous for repeat purchases. Expected: identify an order by the exact checkout payload + Stripe PaymentIntent ID.                                                                                                                                               | 1) Process payments with similar customer/address values.<br>2) Before fix, matching can be ambiguous.<br>3) After fix, lookup includes `original_bag` and `stripe_pid`.                                                                                                                                                      | Fixed              | Added `Order.original_bag` and `Order.stripe_pid` fields (migration `0002_auto_20260226_0822`) and included them in checkout save + webhook lookup/create paths. Retested on 2026-02-26.                                                                                                                                                                                                                                                             |
| 18  | Webhook fallback create path (`/checkout/wh/`)                                                                                      | If checkout form submission fails after payment confirmation, order can be missing in DB. Expected: webhook creates order from PaymentIntent metadata as fallback.                                                                                                                                                 | 1) Simulate missing form submit after payment confirmation.<br>2) Before fix, paid order may not exist in DB.<br>3) After fix, webhook creates order and returns success response.                                                                                                                                            | Fixed              | Implemented webhook fallback creation from metadata bag and shipping/billing details in `checkout/webhook_handler.py`. Retested on 2026-02-26.                                                                                                                                                                                                                                                                                                       |
| 19  | Success toast on profile page (`/profile/`)                                                                                         | Success toast could render checkout bag summary content when viewing profile, which is unrelated and noisy on that page. Expected: profile page toasts should not include bag-summary section.                                                                                                                     | 1) Navigate to `/profile/` and trigger a success message.<br>2) Before fix, toast may include bag/total summary section when `grand_total` is present.<br>3) After fix, bag-summary section is hidden on profile page.                                                                                                        | Fixed              | Updated `templates/includes/toasts/toast_success.html` to gate bag-summary render with `not on_profile_page`, and set `on_profile_page` in `profiles/views.py` context. Retested on 2026-03-03.                                                                                                                                                                                                                                                      |
| 20  | Add Product image handling (`/products/add/`)                                                                                       | Adding a product without uploading an image could trigger an error in product display flow. Expected: product saves successfully without an image and uses placeholder where applicable.                                                                                                                           | 1) Go to `/products/add/`.<br>2) Submit a valid product with no image selected.<br>3) Visit product list/detail and confirm it renders with fallback image handling instead of crashing.                                                                                                                                      | Fixed              | Retested on 2026-03-24 by creating a product without an uploaded image. Product creation succeeded and both product list/detail rendered with the default placeholder image (camera icon) and no errors.                                                                                                                                                                                                                                             |
| 21  | Header Product Management link reverse (`/`)                                                                                        | Homepage failed for superusers with `NoReverseMatch` on `add_product` in account dropdown. Expected: homepage renders and Product Management link resolves safely.                                                                                                                                                 | 1) Log in as superuser.<br>2) Visit `/`.<br>3) Before fix, template can raise `Reverse for 'add_product' not found` from header dropdown URL tag.<br>4) After fix, homepage loads and Product Management link works.                                                                                                          | Fixed              | Updated `templates/base.html` and `templates/includes/mobile-top-header.html` to resolve Product Management URL with a safe fallback order: `add_product`, then `products:add_product`, then `/products/add/`. Retested with `manage.py check` and by reloading `/` on 2026-03-04.                                                                                                                                                                   |
| 22  | Stale dev server URLconf causing false 404 (`/products/edit/<id>/`)                                                                 | Browser showed 404 for `/products/edit/2/` and listed only two products routes, even though code included add/edit/delete patterns. Expected: edit route resolves and redirects unauthenticated users to login.                                                                                                    | 1) Run dev server for a while with route edits in progress.<br>2) Visit `/products/edit/2/`.<br>3) Before fix, browser may show URL pattern list missing add/edit/delete and return 404.<br>4) Restart all runserver processes and retry URL.                                                                                 | Fixed              | Verified `products/urls.py` contains add/edit/delete routes and `reverse('edit_product', args=[2])` resolves. Killed stale `runserver` process (PID `38828`), restarted server from project `.venv`, and retested `/products/edit/2/` to confirm `302` redirect to login (route matched) on 2026-03-04.                                                                                                                                              |
| 23  | Bag size render (`/bag/`)                                                                                                           | Bag page displayed the literal template tag instead of the actual size value. Expected: bag shows the selected size.                                                                                                                                                                                               | 1) Add a sized product to the bag.<br>2) Visit `/bag/`.<br>3) Before fix, size line renders the literal template tag instead of the size value.                                                                                                                                                                               | Fixed              | Updated `bag/templates/bag/bag.html` to keep the size template tag on one line so it renders correctly. Retested on 2026-03-11.                                                                                                                                                                                                                                                                                                                      |
| 24  | Checkout success template regression (`/checkout/checkout_success/`)                                                                | Checkout completion raised `TemplateSyntaxError` (`Invalid block tag on line 76: 'endfor', expected 'elif', 'else' or 'endif'`) when rendering order line items. Expected: success page renders after payment completes.                                                                                           | 1) Complete an order and redirect to `/checkout/checkout_success/<order_number>`.<br>2) Before fix, Django throws a template parsing error referencing line 76 and mismatched block tags.<br>3) After fix, success page renders and displays order summary correctly.                                                         | Fixed              | Rewrote the `item.product_size` conditional block in `checkout/templates/checkout/checkout_success.html` to clean multiline `{% if %} ... {% endif %}` syntax (removed malformed split-tag formatting). Verified with `manage.py check` and page render retest on 2026-03-18.                                                                                                                                                                        |
| 25  | Success email placeholder render (`/checkout/checkout_success/`)                                                                    | Success page showed the literal string `{{ order.email }}` instead of the customer email in the confirmation sentence. Expected: render the actual saved order email address.                                                                                                                                      | 1) Complete checkout and land on `/checkout/checkout_success/<order_number>`.<br>2) Before fix, page text displays `A confirmation email will be sent to {{ order.email }}` literally.<br>3) After fix, sentence shows the real email value.                                                                                  | Fixed              | Normalized the confirmation sentence tag in `checkout/templates/checkout/checkout_success.html` to a clean one-line interpolation (`{{ order.email }}`) to avoid malformed/split template token rendering. Retested on 2026-03-18 with `manage.py check` and checkout success view.                                                                                                                                                                  |
| 26  | Product detail post-add redirect (`/products/<id>/`)                                                                                | Intermittent `500` occurred on product detail immediately after successful Add to Bag redirect. Expected: Add to Bag returns `302` and redirected product detail returns `200`.                                                                                                                                    | 1) Open `/products/2/`.<br>2) Submit Add to Bag.<br>3) Before fix, redirected GET to `/products/2/` intermittently returned `500`.<br>4) After fix, flow remains `302` -> `200` consistently.                                                                                                                                 | Fixed              | Root cause was malformed template control-flow tags in `templates/includes/toasts/toast_success.html` (triggered when success messages rendered after add-to-bag). Corrected template tag structure. Retested in production across product IDs `1-12` on 2026-03-19; sampled flows returned `200/302/200` with no fresh `status=500`/`TemplateSyntaxError` in recent logs.                                                                           |
| 27  | Shared template HTML validation cleanup                                                                                             | W3C validation snapshots showed repeated shared-template issues across multiple pages, mainly invalid `aria-labelledby` usage on generic dropdown containers and heading-order skips in product-management templates. Expected: shared templates use valid markup and pass a fresh validator rerun.                | 1) Review validator findings across `/`, `/products/`, `/products/2/`, `/bag/`, `/checkout/`, `/accounts/login/`, and `/accounts/signup/`.<br>2) Trace repeated issues back to shared navigation templates and product-management headings.<br>3) Apply markup cleanup.<br>4) Revalidate the deployed pages after deployment. | Fixed and verified | Removed invalid `aria-labelledby` attributes from shared dropdown menu containers, replaced product-management `<h5>` subheadings with paragraph text, corrected the style-assistant heading order, and removed the trailing slash from the shared Font Awesome `<link>` tag. Verified with `manage.py check` and a post-deploy W3C validator JSON API rerun on 2026-03-24: all tested pages returned 0 errors, 0 warnings, and 0 info messages.     |
| 28  | Bag size render regression (`/bag/`)                                                                                                | Regression of Bug #23 on production: bag page displayed the literal template tag (`{{ item.size\|upper }}`) instead of rendering the selected size value. Expected: bag shows the actual selected size (or `N/A` when no size applies).                                                                            | 1) Add a sized product to bag on production.<br>2) Visit `/bag/`.<br>3) Observe size line rendering literal template text instead of value.                                                                                                                                                                                   | Fixed              | Referenced Bug #23 and reapplied a defensive template fix in `bag/templates/bag/bag.html` by normalizing the size conditional block to explicit multiline syntax (`{% if item.product.has_sizes and item.size %}{{ item.size\|upper }}{% else %}N/A{% endif %}`). Deployed to Heroku and retested on production on 2026-03-24: bag size now renders correctly.                                                                                       |
| 29  | Homepage CTA contrast (`/`)                                                                                                         | Lighthouse previously reported insufficient contrast on the homepage Shop Now CTA. Expected: button text/background meet at least `4.5:1` for normal text.                                                                                                                                                         | 1) Run Lighthouse on `/` in mobile mode.<br>2) Open Accessibility audits and inspect the colour-contrast finding for `a.shop-now-button`.<br>3) Confirm reported ratio is below expected threshold.<br>4) Apply style update and manually retest CTA contrast and readability.                                                | Fixed              | Updated `.shop-now-button` in `static/css/base.css` on 2026-04-15 to use dark brand text on the gold CTA (including hover/focus/active), improving practical text contrast and resolving the previously tracked issue.                                                                                                                                                                                                                               |
| 30  | Mobile navigation home route (`collapsed main nav`)                                                                                 | On mobile, users had no obvious way to navigate back to Home from the collapsed main menu. Expected: a clear Home link appears at the top of the collapsed navigation list.                                                                                                                                        | 1) Open the site on a mobile viewport (`<992px`).<br>2) Open the hamburger menu.<br>3) Before fix, there is no direct Home item in the main nav list.<br>4) After fix, Home appears as the first nav item and routes to `/`.                                                                                                  | Fixed              | Added a Home nav item at the top of `templates/includes/main-nav.html` using `{% url 'home' %}` (`id="home-link"`), with the existing divider pattern preserved before category/dropdown items.                                                                                                                                                                                                                                                      |
| 31  | Homepage mobile horizontal elastic overflow (`/`)                                                                                   | On iPhone/mobile Safari, the homepage could stretch or rubber-band horizontally while `/products/` remained stable. Expected: homepage stays constrained to the viewport width with no sideways elastic movement.                                                                                                  | 1) Open `/` on iPhone or Safari mobile emulation.<br>2) Swipe horizontally on the homepage.<br>3) Before fix, the page can feel elastically wider than the viewport.<br>4) After fix, the page remains constrained with no horizontal stretch.                                                                                | Fixed              | Updated `static/css/base.css` to apply `overflow-x: hidden` at the root and disable the fixed body background on screens under `992px` with `background-attachment: scroll`. Deployed to Heroku and verified production returned `200` on 2026-03-31.                                                                                                                                                                                                |
| 32  | Order authorisation on success/history views (`/checkout/checkout_success/<order_number>`, `/profile/order_history/<order_number>`) | Order pages were previously fetched by `order_number` alone. Expected: only the same checkout session or the rightful account owner can view an order, and one authenticated user must never be able to reassign another user's order to themselves.                                                               | 1) Attempt to open another order's success/history URL while anonymous or logged in as a different user.<br>2) Confirm unauthorised access is blocked.<br>3) Confirm the rightful owner can still access their order history.<br>4) Confirm guest checkout success still works for the matching session only.                 | Fixed              | Added ownership/session checks in `checkout/views.py` and `profiles/views.py`. `checkout_success` now rejects unauthorised access and no longer reattaches someone else's order to the logged-in user. Added regression tests in `checkout/tests.py` and `profiles/tests.py`. Retested on 2026-04-16 with `manage.py check`, targeted verbose test runs for `checkout.tests` and `profiles.tests`, and full `manage.py test` (`Ran 23 tests`, `OK`). |
| 33  | Password reset link flow (`/accounts/password/reset/key/<uid>-<key>/`)                                                              | Resetting password from emailed link could fail due to a template parsing regression, making the flow appear broken even with a valid link and matching new passwords. Expected: link opens reset form, submit succeeds, and login works with the new password.                                                    | 1) Request a password reset email.<br>2) Open the emailed reset link.<br>3) Before fix, Django raised a template parsing error on `password_reset_from_key` because of malformed tag formatting around `{% endif %}`.<br>4) After fix, form loads and password change completes successfully.                                 | Fixed              | Corrected malformed template tag formatting in `templates/allauth/account/password_reset_from_key.html` so `{% endif %}` is valid. Retested on 2026-04-16 with an end-to-end local flow: reset request -> open emailed link -> set new password -> authenticate with new password succeeds and old password fails.                                                                                                                                   |
| 34  | Product rating validation (`/products/add/`, `/products/edit/<id>/`)                                                                | Rating input accepted values outside the intended `0.00` to `5.00` range. Expected: the form only accepts decimal ratings between 0.00 and 5.00, with a clear error if the value is out of range.                                                                                                                  | 1) Open `/products/add/` or `/products/edit/<id>/`.<br>2) Enter a rating above 5 or below 0.<br>3) Submit the form.<br>4) Confirm the form blocks the save and shows the range message.                                                                                                                                       | Fixed              | Added explicit `ProductForm.rating` validation in `products/forms.py` with `min_value=0`, `max_value=5`, `decimal_places=2`, `step='0.01'`, and a label of `Rating (0.00 - 5.00)`. Also added model validators in `products/models.py`.                                                                                                                                                                                                              |
| 35  | Product price validation and display (`/products/add/`, `/products/edit/<id>/`, product list/detail)                                | Price input and display were not clearly constrained to pounds and pence. Expected: the form accepts decimal prices with at most 2 decimal places, rejects commas, and product prices display with comma separators for thousands when needed.                                                                     | 1) Open `/products/add/` or `/products/edit/<id>/`.<br>2) Enter a price using a comma or more than two decimal places.<br>3) Submit the form and confirm it is rejected with a clear message.<br>4) View product list/detail and confirm values over 999 display with a thousands separator.                                  | Fixed              | Updated `products/forms.py` to label the field `Price (£)`, set `step='0.01'`, and reject commas and more than two decimal places with explicit validation messages. Enabled `django.contrib.humanize` in `fabric_focus/settings.py` and formatted displayed prices with `intcomma` in `products/templates/products/products.html` and `products/templates/products/product_detail.html`.                                                            |
| 36  | Product search results summary (`/products/?q=...`)                                                                                 | The search results summary showed the literal words `search term` instead of the query the user entered, so the page did not clearly tell the user what had been searched. Expected: the results line should show the actual search query in a natural sentence, or just the total count when no search is active. | 1) Visit `/products/?q=soft` or another search query.<br>2) Before the fix, the summary showed a placeholder like `search term` instead of the entered query.<br>3) After the fix, the summary reads `Showing 3 results for "soft"`.                                                                                          | Fixed              | Updated `products/templates/products/products.html` to render a clearer summary line using the actual `search_term`: `Showing {{ products                                                                                                                                                                                                                                                                                                            | length }} result{{ products | length | pluralize }} for "{{ search_term }}"` when searching, and a plain product count otherwise. |
| 37  | Product SKU uniqueness (`/products/add/`, `/products/edit/\<id\>/`)                                                                 | The product form allowed duplicate SKUs, which could create duplicate catalogue entries and confusion in admin management. Expected: SKU values are unique and duplicate entries are rejected with a clear validation message.                                                                                     | 1) Open `/products/add/` or `/products/edit/\<id\>/`.<br>2) Enter a SKU that already exists on another product.<br>3) Submit the form.<br>4) Confirm the form blocks the save and shows the duplicate-SKU message.                                                                                                            | Fixed              | Added `unique=True` to `Product.sku` in `products/models.py`, added duplicate-SKU validation in `products/forms.py`, and created regression coverage in `products/tests.py`. Created migration `products/migrations/0004_alter_product_sku.py` and verified with `python manage.py test products`.                                                                                                                                                   |
| 38  | Dependency: django-countries (Python 3.12 upgrade)                                                                                  | After upgrading to Python 3.12, `python manage.py makemigrations` failed with an import error in `django_countries` due to an outdated version incompatible with Python 3.12. Expected: migrations and management commands run without errors on Python 3.12.                                                      | 1) Upgrade to Python 3.12.<br>2) Run `python manage.py makemigrations`.<br>3) Observe import error in `django_countries`.<br>4) Upgrade `django-countries` and `setuptools`.<br>5) Retry migrations.                                                                                                                          | Fixed              | Upgraded `django-countries` to 8.2.0 and `setuptools` to latest. Updated `requirements.txt` with new versions. Verified `python manage.py makemigrations` and `python manage.py migrate` both succeed on Python 3.12.                                                                                                                                                                                                                                |
| 39  | Dependency: Django compatibility (Python 3.12 upgrade)                                                                              | After upgrading to Python 3.12, Django was incompatible with the new Python version, causing SMTP-based registration emails to fail. Expected: user registration emails send successfully and Django operates normally on Python 3.12.                                                                             | 1) Upgrade to Python 3.12.<br>2) Attempt user registration.<br>3) Observe SMTP/email failure during registration flow.<br>4) Upgrade Django to 4.2.30.<br>5) Retry registration and confirm email is sent.                                                                                                                    | Fixed              | Upgraded Django to 4.2.30. Updated `requirements.txt`. Verified user registration emails send correctly and all management commands run without errors.                                                                                                                                                                                                                                                                                              |
| 40  | Mobile header icon link accessible names (`/`)                                                                                      | Lighthouse reported that the mobile search and account dropdown links did not have discernible names. Expected: icon-only mobile header controls expose clear accessible names to assistive technologies.                                                                                                          | 1) Run Lighthouse mobile on `/`.<br>2) Review the Accessibility audit for "Links do not have a discernible name".<br>3) Confirm `a#mobile-search` and `a#user-options-mobile` are listed before the fix.<br>4) Add accessible names and rerun Lighthouse after deployment.                                                    | Fixed locally      | Added explicit `aria-label` values to the mobile search link, account menu link, bag link, and search submit button in `templates/includes/mobile-top-header.html` on 2026-04-30.                                                                                                                                                                                                                                                                    |

## Testing Table

This table summarises key test cases and their results for core project features.

| Test Case                          | Area / Feature  | Steps / Description                                                                                                                        | Expected Result                                                                          | Actual Result                                                                                                                                                                                                        | Status |
| ---------------------------------- | --------------- | ------------------------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| Homepage loads                     | Home page       | Visit `/`                                                                                                                                  | Page loads, no errors                                                                    | As expected                                                                                                                                                                                                          | Passed |
| Product list loads                 | Products        | Visit `/products/`                                                                                                                         | Product list visible                                                                     | As expected                                                                                                                                                                                                          | Passed |
| Product detail loads               | Products        | Click product from list                                                                                                                    | Detail page visible                                                                      | As expected                                                                                                                                                                                                          | Passed |
| Add to bag                         | Bag             | Add product to bag                                                                                                                         | Bag updates                                                                              | As expected                                                                                                                                                                                                          | Passed |
| Remove from bag                    | Bag             | Remove product from bag                                                                                                                    | Bag updates                                                                              | As expected                                                                                                                                                                                                          | Passed |
| Checkout form renders              | Checkout        | Visit `/checkout/`                                                                                                                         | Form visible                                                                             | As expected                                                                                                                                                                                                          | Passed |
| User registration                  | Accounts        | Register new user                                                                                                                          | Account created                                                                          | As expected                                                                                                                                                                                                          | Passed |
| Login/logout                       | Accounts        | Login and logout flows                                                                                                                     | Auth works                                                                               | As expected                                                                                                                                                                                                          | Passed |
| Admin access                       | Admin           | Login as superuser, visit `/admin/`                                                                                                        | Admin dashboard loads                                                                    | As expected                                                                                                                                                                                                          | Passed |
| Invalid login                      | Accounts        | Attempt login with wrong password                                                                                                          | Error message shown                                                                      | As expected                                                                                                                                                                                                          | Passed |
| Password reset                     | Accounts        | Request password reset email                                                                                                               | Email sent, can reset                                                                    | As expected                                                                                                                                                                                                          | Passed |
| Search products                    | Products        | Use search box with query                                                                                                                  | Filtered results shown                                                                   | As expected                                                                                                                                                                                                          | Passed |
| Empty search                       | Products        | Submit empty search                                                                                                                        | Error message, redirect                                                                  | As expected                                                                                                                                                                                                          | Passed |
| Add product with size              | Bag             | Add product with size to bag                                                                                                               | Size shown in bag                                                                        | As expected                                                                                                                                                                                                          | Passed |
| Remove product with size           | Bag             | Remove sized product from bag                                                                                                              | Bag updates                                                                              | As expected                                                                                                                                                                                                          | Passed |
| Responsive layout (mobile)         | Layout          | View site on mobile device                                                                                                                 | Layout adapts, no overlap                                                                | As expected                                                                                                                                                                                                          | Passed |
| Responsive layout (desktop)        | Layout          | View site on desktop                                                                                                                       | Layout adapts, no overlap                                                                | As expected                                                                                                                                                                                                          | Passed |
| Placeholder image for no product   | Products        | View product with no image                                                                                                                 | Placeholder image shown                                                                  | As expected                                                                                                                                                                                                          | Passed |
| Add-to-bag toast notification      | Bag             | Add item to bag                                                                                                                            | Toast notification appears                                                               | As expected                                                                                                                                                                                                          | Passed |
| Product detail after add redirect  | Products/Bag    | From `/products/<id>/`, submit Add to Bag and follow redirect                                                                              | POST returns `302`; redirected detail returns `200`                                      | As expected                                                                                                                                                                                                          | Passed |
| Remove-from-bag toast notification | Bag             | Remove item from bag                                                                                                                       | Toast notification appears                                                               | As expected                                                                                                                                                                                                          | Passed |
| Admin create product               | Admin           | Create product in admin                                                                                                                    | Product appears in list                                                                  | As expected                                                                                                                                                                                                          | Passed |
| Admin edit product                 | Admin           | Edit product in admin                                                                                                                      | Changes visible in list                                                                  | As expected                                                                                                                                                                                                          | Passed |
| Admin delete product               | Admin           | Delete product in admin                                                                                                                    | Product removed from list                                                                | As expected                                                                                                                                                                                                          | Passed |
| Checkout with empty bag            | Checkout        | Try to checkout with empty bag                                                                                                             | Error message, redirect                                                                  | As expected                                                                                                                                                                                                          | Passed |
| Checkout with filled bag           | Checkout        | Checkout with items in bag                                                                                                                 | Order form shown                                                                         | As expected                                                                                                                                                                                                          | Passed |
| Webhook dedupe on same PI          | Checkout/Stripe | Call `payment_intent.succeeded` twice for same PaymentIntent                                                                               | First call creates order; second verifies existing                                       | As expected                                                                                                                                                                                                          | Passed |
| Webhook fallback order creation    | Checkout/Stripe | Simulate payment confirmed without final form submit                                                                                       | Webhook creates order from metadata                                                      | As expected                                                                                                                                                                                                          | Passed |
| AI assistant disclaimer visibility | AI Assistant    | Open the "What to wear" panel and inspect helper text above the input                                                                      | Disclaimer is clearly visible before submitting chat                                     | As expected                                                                                                                                                                                                          | Passed |
| CSS validation                     | Static files    | W3C CSS Validator on `/`, `/products/`, `/products/2/`, `/bag/`, `/checkout/`, `/accounts/login/`, `/accounts/signup/` (CSS Level 3 + SVG) | No CSS errors found                                                                      | 0 errors on all tested pages; 738 warnings per page (mainly third-party/vendor CSS)                                                                                                                                  | Passed |
| HTML validation                    | Templates       | W3C HTML Validator on `/`, `/products/`, `/products/2/`, `/bag/`, `/checkout/`, `/accounts/login/`, `/accounts/signup/`                    | Valid markup                                                                             | Post-deploy validator rerun on 2026-03-24 returned 0 errors, 0 warnings, and 0 info messages on all tested pages.                                                                                                    | Passed |
| Lighthouse audit                   | Site            | Run Lighthouse on `/`                                                                                                                      | Numeric scores recorded for submission                                                   | Homepage run captured on 2026-03-24: Performance 57, Accessibility 94, Best Practices 100, SEO 91. Final homepage screenshot captured on 2026-04-30: Performance 77, Accessibility 100, Best Practices 100, SEO 100. | Passed |
| Rating validation                  | Products        | Open the add/edit product form and try values outside the 0.00 to 5.00 range                                                               | Form blocks invalid ratings and shows a clear error                                      | As expected                                                                                                                                                                                                          | Passed |
| Price validation and formatting    | Products        | Open the add/edit product form and enter commas or more than 2 decimal places; view prices above 999 on list/detail pages                  | Form rejects invalid price input and displayed prices use comma separators for thousands | As expected                                                                                                                                                                                                          | Passed |
| Search results summary             | Products        | Search for a product and review the results summary text                                                                                   | Summary reads naturally and shows the query clearly when search is active                | As expected                                                                                                                                                                                                          | Passed |
| SKU uniqueness                     | Products        | Open the add/edit product form and enter a SKU that already exists                                                                         | Duplicate SKU is rejected with a clear validation message                                | As expected                                                                                                                                                                                                          | Passed |
