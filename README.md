# Mirc Glow website (mircglow.com)

Static website for Mirc Glow, hosted on Vercel. Customers order with the website checkout (pay online with Razorpay, or Cash on Delivery) or on WhatsApp (+91 99808 81230).

- `content/` – page, article and product text (copied from the old WordPress site)
- `src/` – design (CSS, small script) and page templates
- `wp-content/uploads/` – product photos at the same addresses they had on WordPress
- `build.py` – builds the site into `dist/` (run `python3 build.py`), `check.py` checks links and SEO tags
- `api/` – small server functions for the checkout (Vercel deploys them automatically)
- `dist/` – the finished website that Vercel serves (settings in `vercel.json`)

Every page keeps the address, title and description it had on WordPress, so Google rankings carry over.

## Online checkout

Product pages have **Add to cart** and **Buy now**, with WhatsApp kept as a second way to order. The checkout is at `/checkout/`, the cart at `/cart/`, the confirmation at `/order-success/` (all three are hidden from Google).

- **Cash on Delivery:** the server works out the price, checks the pin code with Delhivery, books the Delhivery parcel (COD amount = order total) and saves the order in the Order Desk with the tracking number (AWB). Print the label from the Delhivery panel. If the booking fails, the order is still saved in the Order Desk with a "⚠ Delhivery booking failed" note so you can book it by hand.
- **Pay online (Razorpay):** the payment is checked with Razorpay on the server, then the order is saved in the Order Desk as PAID. Paid orders are not booked with Delhivery automatically.
- Prices come from the `PRODUCTS` list in `build.py`. `python3 build.py` writes them to `api/_products.json`, which the server uses; the customer's browser never decides the amount. Order numbers start with `MG`. Coupon: `GLOW10` (10% off), set in `COUPONS` in `build.py`.

### Settings in Vercel (Project → Settings → Environment Variables)

| Name | Value |
|---|---|
| `RAZORPAY_KEY_ID` | Razorpay key id (Dashboard → API keys) |
| `RAZORPAY_KEY_SECRET` | Razorpay key secret |
| `DELHIVERY_TOKEN` | Delhivery API token |
| `DELHIVERY_PICKUP` | `mohammed nihal|Beauty Mart` (pickup name as registered in Delhivery) |
| `WEB_ORDER_KEY` | the Order Desk web-order key |
| `ORDERDESK_URL` | optional, default `https://www.skinday.shop` |

Redeploy after adding them. Until Razorpay or Delhivery is set, the cart buttons stay hidden and the site orders on WhatsApp exactly as before. `/api/delhivery-check/` shows whether the Delhivery token works (it books nothing and shows no secrets).
