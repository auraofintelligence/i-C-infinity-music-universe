const STRIPE_API_VERSION = "2026-02-25.clover";
const DEFAULT_ORDER_PAGE_URL = "https://auraofintelligence.github.io/i-C-infinity-music-universe/order.html";

const PACKAGE_MAP = {
  "one-album": {
    name: "One Album Pack",
    amountAud: 20,
    amountCents: 2000,
  },
  "two-album": {
    name: "Two Album Pack",
    amountAud: 35,
    amountCents: 3500,
  },
  "three-album": {
    name: "Three Album Pack",
    amountAud: 45,
    amountCents: 4500,
  },
  "full-archive": {
    name: "Full Music Archive Pack",
    amountAud: 50,
    amountCents: 5000,
  },
};

const ORDER_HEADERS = [
  "createdAt",
  "orderId",
  "status",
  "packageId",
  "packageName",
  "amountAud",
  "paymentMethod",
  "buyerName",
  "buyerEmail",
  "albumChoices",
  "deliveryNotes",
  "sourcePage",
  "stripeSessionId",
  "stripeSessionUrl",
  "paypalUrl",
  "manualPaymentReference",
];

function doPost(e) {
  const fields = e && e.parameter ? e.parameter : {};
  if ((fields.website || "").trim()) {
    return renderMessage_("Order ignored", "The order could not be accepted.");
  }

  const packageId = PACKAGE_MAP[fields.packageId] ? fields.packageId : "full-archive";
  const packageInfo = PACKAGE_MAP[packageId];
  const paymentMethod = (fields.paymentMethod || "stripe").toLowerCase();
  const orderId = "ICI-" + Utilities.formatDate(new Date(), "Australia/Brisbane", "yyyyMMdd-HHmmss") + "-" + Utilities.getUuid().slice(0, 8);
  const createdAt = new Date();
  const buyerEmail = (fields.buyerEmail || "").trim();

  if (!buyerEmail || !(fields.buyerName || "").trim()) {
    return renderMessage_("Missing details", "Please go back and add your name and delivery email.");
  }

  const order = {
    createdAt,
    orderId,
    status: "received",
    packageId,
    packageName: packageInfo.name,
    amountAud: packageInfo.amountAud,
    paymentMethod,
    buyerName: (fields.buyerName || "").trim(),
    buyerEmail,
    albumChoices: (fields.albumChoices || "").trim(),
    deliveryNotes: (fields.deliveryNotes || "").trim(),
    sourcePage: (fields.sourcePage || "").trim(),
    stripeSessionId: "",
    stripeSessionUrl: "",
    paypalUrl: "",
    manualPaymentReference: "",
  };

  const rowNumber = appendOrderRow_(order);

  if (paymentMethod === "stripe") {
    return createStripeCheckout_(order, packageInfo, rowNumber);
  }

  if (paymentMethod === "paypal") {
    const paypalUrl = getScriptProperty_("PAYPAL_URL", "");
    updateOrderRow_(rowNumber, {
      status: paypalUrl ? "paypal_redirect" : "paypal_pending_setup",
      paypalUrl,
    });
    if (paypalUrl) {
      return renderRedirect_(paypalUrl, "Continue to PayPal");
    }
    return renderMessage_("PayPal is nearly ready", "Your order was logged, but the PayPal payment URL has not been added to Apps Script properties yet.");
  }

  const reference = order.orderId;
  updateOrderRow_(rowNumber, {
    status: "awaiting_manual_payment",
    manualPaymentReference: reference,
  });
  return renderManualPayment_(order, reference);
}

function doGet() {
  return renderMessage_("I C. Infinity order endpoint", "This Google Apps Script endpoint is active.");
}

function createStripeCheckout_(order, packageInfo, rowNumber) {
  const secretKey = getRequiredScriptProperty_("STRIPE_SECRET_KEY");
  const orderPageUrl = getScriptProperty_("ORDER_PAGE_URL", DEFAULT_ORDER_PAGE_URL);
  const successUrl = orderPageUrl + "?status=stripe-success&orderId=" + encodeURIComponent(order.orderId);
  const cancelUrl = orderPageUrl + "?status=stripe-cancelled&orderId=" + encodeURIComponent(order.orderId);

  const payload = {
    mode: "payment",
    success_url: successUrl,
    cancel_url: cancelUrl,
    customer_email: order.buyerEmail,
    "line_items[0][price_data][currency]": "aud",
    "line_items[0][price_data][unit_amount]": String(packageInfo.amountCents),
    "line_items[0][price_data][product_data][name]": packageInfo.name,
    "line_items[0][quantity]": "1",
    "metadata[order_id]": order.orderId,
    "metadata[package_id]": order.packageId,
    "metadata[payment_method_choice]": order.paymentMethod,
  };

  const response = UrlFetchApp.fetch("https://api.stripe.com/v1/checkout/sessions", {
    method: "post",
    headers: {
      Authorization: "Bearer " + secretKey,
      "Stripe-Version": STRIPE_API_VERSION,
    },
    payload,
    muteHttpExceptions: true,
  });

  const code = response.getResponseCode();
  const body = response.getContentText();
  const session = parseJson_(body);

  if (code < 200 || code >= 300 || !session.url) {
    updateOrderRow_(rowNumber, {
      status: "stripe_error",
      deliveryNotes: order.deliveryNotes + "\nStripe error: " + body,
    });
    return renderMessage_("Stripe could not start", "Your order was logged, but Stripe returned an error. Please contact Luke before paying.");
  }

  updateOrderRow_(rowNumber, {
    status: "stripe_checkout_created",
    stripeSessionId: session.id || "",
    stripeSessionUrl: session.url || "",
  });

  return renderRedirect_(session.url, "Continue to Stripe Checkout");
}

function appendOrderRow_(order) {
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);
  try {
    const sheet = getOrderSheet_();
    const row = ORDER_HEADERS.map((header) => order[header] || "");
    sheet.appendRow(row);
    return sheet.getLastRow();
  } finally {
    lock.releaseLock();
  }
}

function updateOrderRow_(rowNumber, updates) {
  const sheet = getOrderSheet_();
  const headers = getHeaders_(sheet);
  Object.keys(updates).forEach((key) => {
    const columnIndex = headers.indexOf(key) + 1;
    if (columnIndex > 0) {
      sheet.getRange(rowNumber, columnIndex).setValue(updates[key]);
    }
  });
}

function getOrderSheet_() {
  const spreadsheetId = getRequiredScriptProperty_("SPREADSHEET_ID");
  const sheetName = getScriptProperty_("SHEET_NAME", "Orders");
  const spreadsheet = SpreadsheetApp.openById(spreadsheetId);
  const sheet = spreadsheet.getSheetByName(sheetName) || spreadsheet.insertSheet(sheetName);
  ensureHeaders_(sheet);
  return sheet;
}

function ensureHeaders_(sheet) {
  const headers = getHeaders_(sheet);
  if (headers.join("|") === ORDER_HEADERS.join("|")) return;
  sheet.getRange(1, 1, 1, ORDER_HEADERS.length).setValues([ORDER_HEADERS]);
  sheet.setFrozenRows(1);
}

function getHeaders_(sheet) {
  const lastColumn = Math.max(sheet.getLastColumn(), ORDER_HEADERS.length);
  return sheet.getRange(1, 1, 1, lastColumn).getValues()[0].filter(String);
}

function getRequiredScriptProperty_(key) {
  const value = getScriptProperty_(key, "");
  if (!value) {
    throw new Error("Missing Apps Script property: " + key);
  }
  return value;
}

function getScriptProperty_(key, fallback) {
  return PropertiesService.getScriptProperties().getProperty(key) || fallback;
}

function renderRedirect_(url, label) {
  const safeUrl = escapeHtml_(url);
  const safeLabel = escapeHtml_(label);
  const scriptUrl = JSON.stringify(String(url)).replace(/<\/script/gi, "<\\/script");
  return HtmlService.createHtmlOutput(
    '<!doctype html><html><head><base target="_top"><meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<meta http-equiv="refresh" content="0;url=' + safeUrl + '"></head><body>' +
    '<p><a href="' + safeUrl + '">' + safeLabel + "</a></p>" +
    '<script>window.top.location.href = ' + scriptUrl + ';</script></body></html>'
  );
}

function renderManualPayment_(order, reference) {
  const payIdLabel = getScriptProperty_("PAYID_LABEL", "PayID / bank details will be sent by email.");
  const bankNote = getScriptProperty_("BANK_TRANSFER_NOTE", "Use the order reference when you pay.");
  return renderMessage_(
    "Order logged",
    "Reference: " + reference + "<br>" + escapeHtml_(payIdLabel) + "<br>" + escapeHtml_(bankNote) + "<br>Amount: $" + order.amountAud + " AUD"
  );
}

function renderMessage_(title, message) {
  return HtmlService.createHtmlOutput(
    '<!doctype html><html><head><base target="_top"><meta name="viewport" content="width=device-width, initial-scale=1">' +
    '<style>body{font-family:Arial,sans-serif;max-width:720px;margin:48px auto;padding:0 18px;line-height:1.6}a{font-weight:700}</style>' +
    "</head><body><h1>" + escapeHtml_(title) + "</h1><p>" + message + "</p>" +
    '<p><a href="' + DEFAULT_ORDER_PAGE_URL + '">Back to order page</a></p></body></html>'
  );
}

function escapeHtml_(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function parseJson_(value) {
  try {
    return JSON.parse(value);
  } catch (error) {
    return {};
  }
}
