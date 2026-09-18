# market&co. — Bootstrap E-Commerce Template

A modern, Django-rendered Bootstrap 5 storefront template with New Arrivals,
Gold Jewellery, Diamond Jewellery, Bridal and Collections pages, plus Offers,
and a working "My Cart" (persisted in the browser via `localStorage`).

## Running it

Because the navigation bar and footer live in their **own HTML files**
(`navbar.html` and `footer.html`) and get pulled into every page with
JavaScript's `fetch()`, the site needs to be served over `http://`, not
opened directly as a `file://` path (browsers block `fetch()` on local
files for security reasons).

Easiest way — from inside this folder, run one of:

```bash
# Python 3 (built in on most systems)
python3 -m http.server 8000

# Node (if you have it)
npx serve .
```

Then open **http://localhost:8000/index.html** in your browser.

You can also drop the folder into any static host (Netlify, Vercel,
GitHub Pages, S3, etc.) — no build step required.

## Structure

```
├── index.html          Home page
├── new_arrivals.html   New Arrivals products
├── gold_jewellery.html Gold Jewellery category
├── diamond_jewellery.html Diamond Jewellery category
├── bridal.html         Bridal category
├── collections.html    Jewellery collections
├── offers.html         Jewellery offers page
├── cart.html           My Cart page
├── navbar.html         ★ Shared navigation bar — edit this ONE file
├── footer.html         ★ Shared footer — edit this ONE file
├── css/
│   └── style.css       All design tokens & component styles
└── js/
    ├── include.js      Fetches navbar.html / footer.html into every page
    ├── cart.js          Shared cart logic (add/remove/qty), localStorage-backed
    └── cart-page.js     Renders cart.html from the cart in storage
```

## Editing the navigation

Open `navbar.html`. Every page includes it automatically through
`<div id="navbar-placeholder"></div>` + `js/include.js`, so a change here
appears on every page at once. The same applies to `footer.html`.

To add a new page to the nav:
1. Add a `<li>` / `<a>` to `navbar.html` with a `data-page="yourpage"` attribute.
2. On your new HTML page, set `<body data-page="yourpage">` — the matching
   nav link will automatically get the active-state underline.

## The cart

- Product cards use `data-product` + `data-id`, `data-name`, `data-price`,
  `data-image`, `data-category` attributes; the "+" button (`data-add-to-cart`)
  reads those and adds the item via `window.ShopCart.addItem()`.
- Cart state lives in `localStorage` under the key `marketco_cart`, so it
  persists across page loads and across every page of the site.
- `cart.html` reads that state and renders line items, quantity controls,
  and an order summary (with a simple free-shipping-over-$50 rule).

## Adding products

Create a superuser with `python manage.py createsuperuser`, open `/admin/`,
and use **Products > Add product**. Active products appear in their selected
collection; featured products also appear on the home page.
- Checkout and promo codes are stubbed with a toast message — wire them
  up to your real backend/payment provider.

## Customizing the look

All design tokens (colors, fonts, spacing, radii) are CSS custom
properties at the top of `css/style.css` under `:root`. Fonts are loaded
from Google Fonts (Fraunces / Inter / Space Mono) and Bootstrap 5.3 is
loaded from jsDelivr — both via CDN `<link>`/`<script>` tags in each
page's `<head>`, so an internet connection is needed the first time
pages load (or swap them for local copies if you need to work offline).

Product photos use placeholder images from `picsum.photos` — swap the
`src`/`data-image` URLs for your real product photography before launch.
