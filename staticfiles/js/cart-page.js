/* ============================================================
   cart-page.js
   Renders the cart items + order summary on cart.html using the
   shared ShopCart API from js/cart.js.
   ============================================================ */

(function () {
  var SHIPPING_FLAT = 499;
  var FREE_SHIP_THRESHOLD = 50000;
  var TAX_RATE = 0.0;

  function fmt(n) {
    return "₹" + Math.round(n).toLocaleString("en-IN");
  }

  function render() {
    var cart = window.ShopCart.getCart();
    var itemsWrap = document.getElementById("cartItemsWrap");
    var emptyWrap = document.getElementById("emptyCartWrap");
    var continueWrap = document.getElementById("continueShoppingWrap");
    var summaryCol = document.getElementById("summaryCol");

    if (!itemsWrap) return;

    if (cart.length === 0) {
      itemsWrap.innerHTML = "";
      emptyWrap.classList.remove("d-none");
      continueWrap.classList.add("d-none");
      if (summaryCol) summaryCol.classList.add("d-none");
      return;
    }

    emptyWrap.classList.add("d-none");
    continueWrap.classList.remove("d-none");
    if (summaryCol) summaryCol.classList.remove("d-none");

    itemsWrap.innerHTML = cart
      .map(function (item) {
        return (
          '<div class="cart-row" data-row-id="' + item.id + '">' +
          '<img src="' + item.image + '" alt="' + item.name + '">' +
          '<div class="flex-grow-1">' +
          '<div class="product-cat">' + item.category + "</div>" +
          '<h3 class="product-name mb-1" style="font-size:1rem;">' + item.name + "</h3>" +
          '<span class="swing-tag"><span class="hole"></span>' + fmt(item.price) + "</span>" +
          "</div>" +
          '<div class="d-flex flex-column align-items-end gap-2">' + 
          '<button class="remove-item-btn" data-remove="' + item.id + '" aria-label="Remove item">' +
          '<svg xmlns="http://www.w3.org/2000/svg" width="17" height="17" fill="currentColor" viewBox="0 0 16 16"><path d="M6.5 1h3a.5.5 0 0 1 .5.5v1H6v-1a.5.5 0 0 1 .5-.5ZM11 2.5v-1A1.5 1.5 0 0 0 9.5 0h-3A1.5 1.5 0 0 0 5 1.5v1H1.5a.5.5 0 0 0 0 1h.538l.853 10.66A2 2 0 0 0 4.885 16h6.23a2 2 0 0 0 1.994-1.84L13.962 3.5H14.5a.5.5 0 0 0 0-1H11Zm1.958 1-.846 10.58a1 1 0 0 1-.997.92h-6.23a1 1 0 0 1-.997-.92L3.042 3.5h9.916Z"/></svg>' +
          "</button>" +
          '<div class="qty-control">' +
          '<button data-qty-down="' + item.id + '" aria-label="Decrease quantity">-</button>' +
          '<input type="text" value="' + item.qty + '" data-qty-input="' + item.id + '" readonly>' +
          '<button data-qty-up="' + item.id + '" aria-label="Increase quantity">+</button>' +
          "</div>" +
          '<strong style="font-family: var(--font-mono);">' + fmt(item.price * item.qty) + "</strong>" +
          "</div>" +
          "</div>"
        );
      })
      .join("");

    updateSummary();
  }

  function updateSummary() {
    var subtotal = window.ShopCart.getSubtotal();
    var shipping = subtotal === 0 || subtotal >= FREE_SHIP_THRESHOLD ? 0 : SHIPPING_FLAT;
    var tax = subtotal * TAX_RATE;
    var total = subtotal + shipping + tax;

    var subEl = document.getElementById("sumSubtotal");
    var shipEl = document.getElementById("sumShipping");
    var taxEl = document.getElementById("sumTax");
    var totalEl = document.getElementById("sumTotal");

    if (subEl) subEl.textContent = fmt(subtotal);
    if (shipEl) shipEl.textContent = shipping === 0 ? "Free" : fmt(shipping);
    if (taxEl) taxEl.textContent = fmt(tax);
    if (totalEl) totalEl.textContent = fmt(total);
  }

  document.addEventListener("click", function (e) {
    var removeId = e.target.closest("[data-remove]");
    var qtyUp = e.target.closest("[data-qty-up]");
    var qtyDown = e.target.closest("[data-qty-down]");
    var checkoutBtn = e.target.closest("#checkoutBtn");
    var clearCartBtn = e.target.closest("#clearCartBtn");
    var promoBtn = e.target.closest("#applyPromoBtn");

    if (removeId) {
      window.ShopCart.removeItem(removeId.getAttribute("data-remove"));
      render();
    }
    if (qtyUp) {
      var idUp = qtyUp.getAttribute("data-qty-up");
      var cartUp = window.ShopCart.getCart();
      var itemUp = cartUp.find(function (i) { return i.id === idUp; });
      if (itemUp) window.ShopCart.setQty(idUp, itemUp.qty + 1);
      render();
    }
    if (qtyDown) {
      var idDown = qtyDown.getAttribute("data-qty-down");
      var cartDown = window.ShopCart.getCart();
      var itemDown = cartDown.find(function (i) { return i.id === idDown; });
      if (itemDown && itemDown.qty > 1) window.ShopCart.setQty(idDown, itemDown.qty - 1);
      else if (itemDown && itemDown.qty === 1) window.ShopCart.removeItem(idDown);
      render();
    }
    if (checkoutBtn) {
      e.preventDefault();
      if (window.ShopCart.getCount() === 0) return;
      window.ShopCart.showToast("This is a template — hook up a real checkout flow here.");
    }
    if (clearCartBtn) {
      e.preventDefault();
      window.ShopCart.clearCart();
      render();
    }
    if (promoBtn) {
      e.preventDefault();
      window.ShopCart.showToast("Promo codes aren't wired up in this template yet.");
    }
  });

  document.addEventListener("DOMContentLoaded", render);
})();
