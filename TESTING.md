# Testing

This document outlines how I test Fabric Focus to ensure the project functions as intended, the user experience is consistent across devices and browsers, and core flows (browsing products and account sign-in/sign-out) behave predictably.

The testing approach follows a combination of **Behaviour-Driven Development (BDD)** and **Test-Driven Development (TDD)** principles:

- **BDD (Behaviour-Driven Development):** Focused on real-world user stories, such as *“As a visitor, I want to view the products list so I can browse what’s available.”*
- **TDD (Test-Driven Development):** Where automated tests exist (or are added), tests are written first to encourage correct, maintainable code. (Currently, `home/tests.py` and `products/tests.py` are placeholders, so most validation is manual.)

Both **manual** and **automated** testing methods may be used to validate the functionality, usability, and accessibility of the application.

Key areas covered in testing include:
- Navigation and URL routing (home, products, and accounts routes)
- Product listing template rendering (name/price/rating, and image handling)
- Authentication flows (sign up, login, logout) via Django Allauth
- Django admin checks for product/category management (models are registered in the admin)
- Cross-browser and mobile responsiveness (Bootstrap layout)

Current implementation notes (as of this version of the repo):
- The Products app includes a list view and template; a product detail route/view is present but appears incomplete, so I focus manual testing on the list page first.
- The products template references a placeholder image (`MEDIA_URL + noimage.png`) when a product has no image; I need a placeholder file in `media/` if I want that fallback to work.

For each user story, **black box testing** is applied — evaluating the system purely from the user’s perspective without needing knowledge of internal code logic.

All discovered bugs, fixes, and retests should be documented throughout this file.

For additional project details and technical information, including instructions on running the site, please refer to the [README.md](./README.md)

- [Testing](#testing)
  - [Responsiveness Testing](#responsiveness-testing)
  - [HTML Validator Testing](#html-validator-testing)
  - [CSS Validator Testing](#css-validator-testing)
  - [Lighthouse Testing](#lighthouse-testing)
- [User Stories](#user-stories)
  - [1. Browse Products](#1-browse-products)
  - [2. View Product Details (If/When Implemented)](#2-view-product-details-ifwhen-implemented)
  - [3. Create Account / Login / Logout](#3-create-account--login--logout)
- [Bug Tracker](#bug-tracker)


----

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
| _TBC_ | _TBC_ | _TBC_ | _TBC_ | _TBC_ |

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

- Home page: _TBC_
- Products list: _TBC_
- Accounts pages: _TBC_

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

- `static/css/base.css`: _TBC_

----

## Lighthouse Testing

Lighthouse (Chrome DevTools) audits pages for performance, accessibility, best practices, and SEO.

**How to run Lighthouse:**

1. Open Chrome DevTools (F12).
2. Go to the “Lighthouse” tab.
3. Run audits on key pages (at minimum: `/` and `/products/`).
4. Record scores and any key recommendations.

**Results (I record scores here):**

| Page | Performance | Accessibility | Best Practices | SEO |
| ---- | ----------: | ------------: | -------------: | --: |
| `/` | _TBC_ | _TBC_ | _TBC_ | _TBC_ |
| `/products/` | _TBC_ | _TBC_ | _TBC_ | _TBC_ |

Notes:

- Scores can vary between runs (network conditions, cold cache, background processes).
- For consistency, I run audits in an Incognito window with extensions disabled.

---

# User Stories

## 1. Browse Products

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

## 2. View Product Details (If/When Implemented)

**Story:**
As a visitor, I want to click a product and view its details so that I can learn more before purchasing.

**Acceptance criteria:**

- Given I am on the products list
- When I click a product
- Then I am taken to a product detail page
- And I can see the product’s name, description, price, and image (if available)

**Notes:**

- A product detail route/view is present in the project, but it may require completion/fixes before I can fully test this story end-to-end.

---

## 3. Create Account / Login / Logout

**Story:**
As a visitor, I want to create an account and log in so that I can access account-only features.

**Acceptance criteria:**

- Given I visit `/accounts/signup/`
- When I submit a valid registration form
- Then an account is created (and I’m either signed in or prompted to verify/sign in)

- Given I have an account
- When I sign in at `/accounts/login/`
- Then I can log out successfully

**Bug tracking / notes:**

- See the Bug Tracker section at the bottom of this document.

---

# Bug Tracker

I log bugs here as I find them during manual testing and validation.

How I use this table:

- **ID:** incremental number
- **Area/Feature:** where the issue occurs (page, flow, component)
- **Description:** what happened + what I expected
- **Steps to Reproduce:** clear steps from a fresh page load
- **Status:** Open / In Progress / Fixed / Retest Needed
- **Fix Summary:** short note on what I changed (file/symbol if useful)

| ID | Area / Feature | Description | Steps to Reproduce | Status | Fix Summary |
| -- | -------------- | ----------- | ------------------ | ------ | ---------- |
| 1 | _TBC_ | _TBC_ | _TBC_ | Open | _TBC_ |
| 2 | _TBC_ | _TBC_ | _TBC_ | Open | _TBC_ |



