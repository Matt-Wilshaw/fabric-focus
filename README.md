
# Fabric-Focus

## Introduction

Fabric-Focus is about performance, comfort, and style. By combining carefully selected fabrics, modern designs, and sport-specific functionality, our clothing is made to support you through every workout and active moment.

Whether you're training hard at the gym, heading out for a run, or looking for everyday athletic wear, Fabric-Focus offers reliable, high-quality sportswear designed to move with you. From breathable materials to durable construction, we focus on the details that help you feel confident, comfortable, and ready to perform.

## Live Demo

- Hosted on Heroku: https://fabric-focus-f1a8e9ed6562.herokuapp.com/



## Requirements

This project uses the following key software and Python packages:

- Python 3.x
- Django 3.2.25
- django-allauth
- django-crispy-forms
- Pillow
- Bootstrap (via CDN)
- Other dependencies listed in requirements.txt

## Table of Contents

- [Fabric-Focus](#fabric-focus)
- [Requirements](#requirements)
- [Table of Contents](#table-of-contents)
- [Jesse James Garrett: The Five Planes of User Experience](#jesse-james-garrett-the-five-planes-of-user-experience)
- [Project: Fabric-Focus (Sportswear Clothing Shop)](#project-fabric-focus-sportswear-clothing-shop)
- [1. Strategy Plane](#1-strategy-plane)
- [2. Scope Plane](#2-scope-plane)
- [3. Structure Plane](#3-structure-plane)
- [4. Skeleton Plane](#4-skeleton-plane)
- [5. Surface Plane](#5-surface-plane)
- [User Stories](#user-stories)
- [Installation / Setup](#installation--setup)
- [Stripe testing (Stripe CLI - Windows)](#stripe-testing-stripe-cli---windows)
- [Frontend](#frontend)


## Jesse James Garrett: The Five Planes of User Experience
### Project: Fabric-Focus (Sportswear Clothing Shop)

### 1. Strategy Plane
The goal of Fabric-Focus is to provide users with a convenient and engaging online platform for purchasing sportswear. The current implementation focuses on secure account access, product discovery, bag management, and checkout.

From a business perspective, Fabric-Focus aims to build brand credibility and encourage repeat purchases.

---

### 2. Scope Plane
The scope plane defines the functional and content requirements of the Fabric-Focus website.

**Functional requirements currently implemented include:**
- User registration and login system  
- Secure user accounts  
- Browsing products by category  
- Viewing individual product pages  
- Adding items to a shopping cart  
- Checkout functionality  

**Planned/future requirements include:**
- Leaving product reviews and ratings  
- Commenting on products or reviews (authenticated users only)  

**Content requirements include:**
- Product descriptions focusing on fabric quality and performance  
- Brand and company information  
- Clear feedback messages (e.g. login errors, successful submissions)  

---

### 3. Structure Plane
The structure plane focuses on how information is organised and how users move through the website.

Fabric-Focus follows a standard e-commerce structure:
- Home -> Categories -> Product Page  
- Product Page -> Bag -> Checkout  
- Login/Register -> User Account  

---

### 4. Skeleton Plane
The skeleton plane addresses layout, interface design, and interaction elements.

- Navigation and account access are placed consistently across all pages  
- Product pages prioritise images, pricing, size selection, and "Add to Cart" buttons  
- Error and success messages guide users through interactions  

This layout reduces confusion and improves usability.

---

### 5. Surface Plane
The surface plane focuses on the visual design and overall aesthetic of Fabric-Focus.

The interface uses:
- A modern, sporty colour palette  
- Clean typography for readability  
- Visual hierarchy to highlight key actions  
- Consistent styling across product listings and forms  

The design supports both usability and brand identity, creating a professional and engaging experience suitable for an academic project.

## User Stories

- **Authentication & Account**
  - [x] Visitor: create an account to save details and view orders.
  - [x] Registered user: log in with email/password to access the account.
  - [x] Registered user: reset password via email to regain access.
  - [ ] Account holder: update profile (name, address, phone) for correct shipping.
  - [ ] Account holder: manage multiple shipping addresses.
  - [ ] Account holder: manage saved payment methods securely.
  - [ ] Admin: deactivate/reactivate user accounts to manage abuse.

- **Catalogue, Search & Navigation**
  - [x] Shopper: browse categories (men/women/kids/gear) to discover items.
  - [x] Shopper: search with filters (size, colour, brand, price) to narrow results.
  - [x] Shopper: sort results (relevance, price, newest, rating) to prioritise listings.
  - [ ] Shopper: use pagination or infinite scroll for large result sets.

- **Product Pages & Reviews**
  - [x] Shopper: view product pages with images, specs, size charts, and availability.
  - [ ] Shopper: read customer reviews and average ratings to assess fit and quality.
  - [ ] Authenticated user: post reviews (rating, text, photos) to share feedback.
  - [ ] Shopper: see recommended/related products for discovery.
  - [ ] Admin: moderate or remove abusive reviews.

- **Cart & Checkout**
  - [x] Shopper: add/remove items and change quantities in the cart.
  - [ ] Shopper: save and retrieve cart contents when logged in.
  - [x] Shopper: complete a multi-step checkout (shipping -> payment -> review).
  - [x] Shopper: view shipping cost estimates before checkout.
  - [ ] Shopper: apply discount codes and see adjusted totals.
  - [ ] Shopper: choose saved or enter new addresses at checkout.

- **Payments & Security**
  - [x] Shopper: pay securely (card, Apple/Google Pay, PayPal) using tokenised processing.
  - [x] Shopper: receive order confirmation emails/receipts after payment.
  - [ ] Admin: view payment status and retry failed payments.

- **Orders & Fulfilment**
  - [ ] User: view order history with statuses (processing, shipped, delivered).
  - [ ] User: access shipment tracking links for shipped orders.
  - [ ] User: request returns and view return status and instructions.
  - [ ] Staff: use an orders dashboard to pick, pack, and update shipment status.

- **Notifications & Communication**
  - [x] User: receive emails for order receipt, shipping updates, and delivery.
  - [ ] User: opt into SMS/email delivery updates.

- **Admin & Content Management**
  - [x] Admin: add/edit/remove products, prices, images, and inventory.
  - [ ] Admin: create and manage discount codes and promotions.
  - [ ] Admin: view sales reports and low-stock alerts.
  - [ ] Admin: configure role-based access for staff accounts.

- **User Experience & Accessibility**
  - [x] Shopper: experience responsive pages that work on mobile devices.
  - [ ] Shopper: access clear size guidance and an easy returns process.
  - [ ] User: use accessible UI (keyboard navigation, screen-reader support).

- **Performance, Privacy & Compliance**
  - [x] Stakeholder: ensure fast page loads and CDN for static assets.
  - [ ] User: control personal data (consent, export, delete) for GDPR/CCPA.
  - [ ] Admin: maintain secure audit logging for critical actions.

- **Analytics & Growth**
  - [ ] Marketer: add tracking and analytics to measure conversions.
  - [ ] Marketer: capture emails and run abandoned-cart recovery campaigns.

- **Extras / Future**
  - [ ] Shopper: create wishlists and gift registries.
  - [ ] Shopper: subscribe to back-in-stock alerts for out-of-stock items.



## Installation / Setup

Follow these steps to set up Fabric-Focus locally:

### 1. Clone the repository
```bash
git clone https://github.com/your-username/fabric-focus.git
cd fabric-focus
```

### 2. Create a virtual environment (optional but recommended)
```bash
python -m venv .venv
# Activate it (Windows):
.venv\Scripts\activate
# Activate it (macOS/Linux):
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Apply database migrations
```bash
python manage.py migrate
```

### 5. Create a superuser (optional, for admin access)
```bash
python manage.py createsuperuser
```

### 6. Run the development server
```bash
python manage.py runserver
```

## AI Style Assistant (What to Wear)

This project includes a custom "What to wear" assistant widget that talks to an AI model through a Django endpoint. The key idea is to keep the API key server-side and let the browser call your own endpoint.

**Decision summary**
- Custom integration keeps the widget fully on-brand and lets us add product-aware logic later.
- API keys are never exposed in the browser.

**How it works**
1. The widget in `templates/base.html` sends a POST request to `/style-assistant/`.
2. Django routes that to `home/views.py`, which calls the OpenAI Responses API.
3. The view returns JSON back to the widget.

**Configuration**
- Set `OPENAI_API_KEY` in your environment (server-side only).
- Optional: set `OPENAI_MODEL` to override the default (see `fabric_focus/settings.py`).

**Notes**
- If the API key is missing, the widget falls back to simple keyword-based responses.

### Stripe testing (Stripe CLI - Windows)

If you want to test Stripe webhooks locally using the Stripe CLI on Windows, follow these steps.

Part 1 - Download Stripe CLI

1. Go to: https://docs.stripe.com/stripe-cli?install-method=windows and download the latest Windows zip (filename ending in `windows_x86_64.zip`).
2. Open your Downloads folder and extract the zip.
3. When prompted, extract into a new folder such as `Documents\stripe-cli`.

Part 2 - Add Stripe to PATH

1. Open the `stripe-cli` folder and copy the full path from the Explorer address bar.
2. Press Win + R, type `sysdm.cpl`, and press Enter.
3. In System Properties -> Advanced -> Environment Variables, select `Path` (under System variables) and click `Edit.` -> `New`.
4. Paste the `stripe-cli` folder path (remove any surrounding quotes) and click `OK` to save.

Part 3 - Verify configuration and log in

1. Restart your machine (or restart your terminal session).
2. Open a terminal in this project and run:
```powershell
stripe version
stripe login
```
Follow the browser steps to authenticate (you may need to verify via email). Keys are valid for 90 days.

3. Start listening and forward webhooks to your local Django server:
```powershell
stripe listen --forward-to http://localhost:8000/checkout/wh/
```

4. Copy the printed webhook signing secret (starts with `whsec_`) and set it for your session:
```powershell
$env:STRIPE_PUBLIC_KEY = 'pk_test_...'
$env:STRIPE_SECRET_KEY = 'sk_test_...'
$env:STRIPE_WH_SECRET  = 'whsec_...'
```
To persist values across sessions use `setx` (requires restart):
```powershell
setx STRIPE_PUBLIC_KEY "pk_test_..."
setx STRIPE_SECRET_KEY "sk_test_..."
setx STRIPE_WH_SECRET  "whsec_..."
```

5. Trigger test events:
```powershell
stripe trigger payment_intent.succeeded
```

Notes:
- Do NOT commit real secret keys to the repository. Add them to a local `.env` or `env.py` for development.
- Ensure the Django dev server is running and the webhook view (`/checkout/wh/`) is reachable.

### Frontend

This repository is Django-rendered and does not include a separate `frontend/` React app.


