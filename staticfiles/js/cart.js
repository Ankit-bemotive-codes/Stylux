/* ============================================================
   cart.js
   Minimal shared cart, persisted in localStorage so it carries
   across every page of the template. Exposed as window.ShopCart.
   ============================================================ */

window.ShopCart = (function () {
  var STORAGE_KEY = "groupb_cart";

  function readCart() {
    try {
      var raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : [];
    } catch (e) {
      return [];
    }
  }

  function writeCart(cart) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(cart));
    updateBadge();
  }

  function normalizeQty(qty) {
    var parsed = Number(qty);
    return Number.isFinite(parsed) && parsed > 0 ? Math.floor(parsed) : 1;
  }

  function addItem(product) {
    if (!product || !product.id || !product.name) return readCart();
    var price = Number(product.price);
    if (!Number.isFinite(price) || price < 0) return readCart();
    var cart = readCart();
    var existing = cart.find(function (i) { return i.id === product.id; });
    if (existing) {
      existing.qty = normalizeQty(existing.qty) + normalizeQty(product.qty);
    } else {
      cart.push({
        id: product.id,
        name: product.name,
        price: price,
        image: product.image,
        category: product.category || "",
        qty: normalizeQty(product.qty),
      });
    }
    writeCart(cart);
    return cart;
  }

  function removeItem(id) {
    var cart = readCart().filter(function (i) { return i.id !== id; });
    writeCart(cart);
    return cart;
  }

  function setQty(id, qty) {
    var cart = readCart();
    var item = cart.find(function (i) { return i.id === id; });
    if (item) {
      item.qty = normalizeQty(qty);
    }
    writeCart(cart);
    return cart;
  }

  function clearCart() {
    writeCart([]);
  }

  function getCount() {
    return readCart().reduce(function (sum, i) { return sum + normalizeQty(i.qty); }, 0);
  }

  function getSubtotal() {
    return readCart().reduce(function (sum, i) { return sum + normalizeQty(i.qty) * Number(i.price || 0); }, 0);
  }

  function updateBadge() {
    var count = getCount();
    document.querySelectorAll("#navCartCount").forEach(function (el) {
      el.textContent = count;
      el.style.display = count > 0 ? "flex" : "none";
    });
  }

  function showToast(message) {
    var wrap = document.getElementById("cartToastWrap");
    if (!wrap) return;
    var toastEl = document.createElement("div");
    toastEl.className = "toast align-items-center text-bg-dark border-0";
    toastEl.setAttribute("role", "alert");
    toastEl.innerHTML =
      '<div class="d-flex">' +
      '<div class="toast-body" style="font-family: Inter, sans-serif;">' + message + "</div>" +
      '<button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>' +
      "</div>";
    wrap.appendChild(toastEl);
    var toast = new bootstrap.Toast(toastEl, { delay: 2200 });
    toast.show();
    toastEl.addEventListener("hidden.bs.toast", function () { toastEl.remove(); });
  }

  // Wire up any [data-add-to-cart] buttons found anywhere on the page.
  function bindAddToCartButtons(root) {
    (root || document).querySelectorAll("[data-add-to-cart]").forEach(function (btn) {
      if (btn.dataset.bound) return;
      btn.dataset.bound = "true";
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        var card = btn.closest("[data-product]");
        if (!card) return;
        addItem({
          id: card.dataset.id,
          name: card.dataset.name,
          price: card.dataset.price,
          image: card.dataset.image,
          category: card.dataset.category,
          qty: 1,
        });
        showToast(card.dataset.name + " added to your cart");
      });
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    updateBadge();
    bindAddToCartButtons(document);
  });

  return {
    addItem: addItem,
    removeItem: removeItem,
    setQty: setQty,
    clearCart: clearCart,
    getCart: readCart,
    getCount: getCount,
    getSubtotal: getSubtotal,
    updateBadge: updateBadge,
    showToast: showToast,
    bindAddToCartButtons: bindAddToCartButtons,
  };
})();
