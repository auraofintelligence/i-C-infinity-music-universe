# I C. Infinity Order Flow

This is the private money-path scaffold for the public download pages.

## Shape

1. The order section on `downloads.html` collects package, buyer, album choice, and payment method.
2. Google Apps Script receives the form post.
3. Apps Script writes a row to the private Google Sheet.
4. If the buyer chooses Stripe, Apps Script creates a Stripe Checkout Session and redirects them to Stripe.
5. If the buyer chooses PayPal or PayID / bank transfer, Apps Script logs the order and shows the manual payment path.

No card details are collected on GitHub Pages or stored in Google Sheets.

## Apps Script Setup

1. Create or use a Google Sheet with the headers from `order-sheet-template.csv`.
2. Open Apps Script and paste `google-apps-script/Code.gs`.
3. Add these Script Properties:

| Property | Required | Notes |
| --- | --- | --- |
| `SPREADSHEET_ID` | yes | The private Google Sheet ID. |
| `SHEET_NAME` | no | Defaults to `Orders`. |
| `STRIPE_SECRET_KEY` | yes for Stripe | Use the Stripe secret key. Do not put it in the public repo. |
| `ORDER_PAGE_URL` | no | Defaults to the order section on the public `downloads.html`. |
| `PAYPAL_URL` | no | PayPal payment link or profile URL. |
| `PAYID_LABEL` | no | Public-facing PayID label or email/phone once final. |
| `BANK_TRANSFER_NOTE` | no | Bank-transfer instructions. |

4. Deploy Apps Script as a web app:
   - Execute as: Me
   - Who has access: Anyone
5. Copy the web app URL into `assets/js/order-config.js` as `appsScriptEndpoint`.

## Stripe Notes

This uses Stripe Checkout Sessions with the latest pinned API version in the script. The public site never handles card data.

Later, add a Stripe webhook if you want automatic Sheet status updates after payment success. Until then, Stripe orders are logged when checkout is created and payment can be confirmed in Stripe before delivery.
