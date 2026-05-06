document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("[data-order-form]");
  if (!(form instanceof HTMLFormElement)) return;

  const packages = {
    "one-album": {
      name: "One Album Pack",
      price: 20,
      hint: "Tell me which album you want.",
    },
    "two-album": {
      name: "Two Album Pack",
      price: 35,
      hint: "Tell me the two albums you want.",
    },
    "three-album": {
      name: "Three Album Pack",
      price: 45,
      hint: "Usually Songs of Straddie, Chronicles, and Starseed Code.",
    },
    "full-archive": {
      name: "Full Music Archive Pack",
      price: 50,
      hint: "Include full archive unless you want a custom variation.",
    },
  };

  const aliases = {
    one: "one-album",
    two: "two-album",
    three: "three-album",
    full: "full-archive",
    archive: "full-archive",
  };

  const config = window.IC_INFINITY_ORDER_CONFIG || {};
  const endpoint = (config.appsScriptEndpoint || "").trim();
  const select = form.querySelector("[data-package-select]");
  const summary = form.querySelector("[data-order-summary]");
  const status = form.querySelector("[data-order-status]");
  const albumChoices = form.querySelector("[data-album-choices]");
  const sourcePage = form.querySelector("[data-source-page]");
  const submit = form.querySelector("[data-order-submit]");
  const params = new URLSearchParams(window.location.search);

  const normalisePackage = (value) => {
    const clean = (value || "").toLowerCase().trim();
    return packages[clean] ? clean : aliases[clean] || "full-archive";
  };

  const selectedFromUrl = normalisePackage(params.get("package") || params.get("pack"));
  if (select instanceof HTMLSelectElement) {
    select.value = selectedFromUrl;
  }

  if (sourcePage instanceof HTMLInputElement) {
    sourcePage.value = window.location.href;
  }

  if (endpoint) {
    form.action = endpoint;
  } else if (submit instanceof HTMLButtonElement) {
    submit.disabled = true;
  }

  const updateSummary = () => {
    if (!(select instanceof HTMLSelectElement)) return;
    const item = packages[normalisePackage(select.value)];
    if (summary) {
      summary.innerHTML = `<strong>${item.name} - $${item.price} AUD</strong><br>${item.hint}`;
    }
    if (albumChoices instanceof HTMLTextAreaElement) {
      albumChoices.placeholder = item.hint;
    }
  };

  const updatePaymentHint = () => {
    const checked = form.querySelector("input[name='paymentMethod']:checked");
    const method = checked instanceof HTMLInputElement ? checked.value : "stripe";
    if (!status) return;

    if (!endpoint) {
      status.textContent = "Order backend not connected yet. Deploy the Google Apps Script web app, then paste its URL into assets/js/order-config.js.";
      return;
    }

    if (method === "stripe") {
      status.textContent = "Stripe will open a hosted checkout page after the order is logged.";
    } else if (method === "paypal") {
      status.textContent = "PayPal will open after the order is logged.";
    } else {
      status.textContent = "PayID / bank transfer instructions will show after the order is logged.";
    }
  };

  select?.addEventListener("change", updateSummary);
  form.querySelectorAll("input[name='paymentMethod']").forEach((input) => {
    input.addEventListener("change", updatePaymentHint);
  });

  form.addEventListener("submit", (event) => {
    const honey = form.querySelector("input[name='website']");
    if (honey instanceof HTMLInputElement && honey.value.trim()) {
      event.preventDefault();
      return;
    }

    if (!endpoint) {
      event.preventDefault();
      updatePaymentHint();
    }
  });

  updateSummary();
  updatePaymentHint();
});
