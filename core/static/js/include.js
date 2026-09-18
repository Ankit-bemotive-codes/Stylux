/* ============================================================
   include.js
   Initializes shared Django-rendered navigation and footer elements.
   ============================================================ */

(function () {
  function highlightActiveLink() {
    var current = document.body.getAttribute("data-page");
    document.querySelectorAll(".shop-nav-link").forEach(function (link) {
      if (link.getAttribute("data-page") === current) {
        link.classList.add("active");
        link.setAttribute("aria-current", "page");
      }
    });
  }

  function updateThemeToggle() {
    var isDark = document.documentElement.getAttribute("data-theme") === "dark";
    document.querySelectorAll(".theme-toggle").forEach(function (button) {
      button.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
      button.setAttribute("title", isDark ? "Switch to light mode" : "Switch to dark mode");
    });
  }

  function toggleTheme() {
    var isDark = document.documentElement.getAttribute("data-theme") === "dark";
    document.documentElement.setAttribute("data-theme", isDark ? "light" : "dark");
    localStorage.setItem("theme", isDark ? "light" : "dark");
    updateThemeToggle();
  }

  function initScrollReveal() {
    var revealItems = document.querySelectorAll(".reveal-on-scroll");
    if (!revealItems.length) return;

    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches || !("IntersectionObserver" in window)) {
      revealItems.forEach(function (item) { item.classList.add("is-visible"); });
      return;
    }

    revealItems.forEach(function (item, index) {
      item.style.transitionDelay = Math.min(index * 45, 240) + "ms";
    });

    var observer = new IntersectionObserver(function (entries, revealObserver) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        revealObserver.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

    revealItems.forEach(function (item) { observer.observe(item); });
  }

  function initParallax() {
    var parallaxItems = document.querySelectorAll("[data-parallax]");
    if (!parallaxItems.length || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

    parallaxItems.forEach(function (item) {
      item.dataset.parallaxStart = item.getBoundingClientRect().top + window.scrollY;
    });

    var ticking = false;
    function updateParallax() {
      parallaxItems.forEach(function (item) {
        var speed = Number(item.getAttribute("data-parallax")) || 0;
        var start = Number(item.dataset.parallaxStart) || 0;
        var offset = (window.scrollY - start) * speed;
        item.style.transform = "translate3d(0, " + Math.round(offset) + "px, 0)";
      });
      ticking = false;
    }

    function requestParallaxUpdate() {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(updateParallax);
    }

    window.addEventListener("scroll", requestParallaxUpdate, { passive: true });
    window.addEventListener("resize", requestParallaxUpdate, { passive: true });
    requestParallaxUpdate();
  }

  function initSearchSuggestions() {
    document.querySelectorAll(".shop-search").forEach(function (form) {
      var input = form.querySelector("input[type=search]");
      var panel = form.querySelector(".search-suggestions");
      var source = form.querySelectorAll("[data-search-product]");
      if (!input || !panel || !source.length) return;

      var products = Array.prototype.map.call(source, function (item) {
        return { name: item.dataset.name || "", category: item.dataset.category || "" };
      });
      var highlighted = -1;

      function closeSuggestions() {
        panel.classList.remove("is-open");
        panel.innerHTML = "";
        highlighted = -1;
      }

      function renderSuggestions() {
        var query = input.value.trim().toLowerCase();
        if (!query) return closeSuggestions();
        var matches = products.filter(function (product) {
          return (product.name + " " + product.category).toLowerCase().indexOf(query) !== -1;
        }).slice(0, 6);
        panel.innerHTML = "";
        if (!matches.length) return closeSuggestions();
        var count = document.createElement("div");
        count.className = "search-live-count";
        count.textContent = matches.length + (matches.length === 1 ? " live result" : " live results");
        panel.appendChild(count);
        matches.forEach(function (product, index) {
          var option = document.createElement("button");
          option.type = "button";
          option.className = "search-suggestion";
          option.setAttribute("role", "option");
          option.dataset.index = index;
          option.innerHTML = "<span></span><small></small>";
          option.querySelector("span").textContent = product.name;
          option.querySelector("small").textContent = product.category;
          option.addEventListener("mousedown", function (event) { event.preventDefault(); });
          option.addEventListener("click", function () {
            input.value = product.name;
            form.submit();
          });
          panel.appendChild(option);
        });
        highlighted = -1;
        panel.classList.add("is-open");
      }

      input.addEventListener("input", renderSuggestions);
      input.addEventListener("keydown", function (event) {
        var options = panel.querySelectorAll(".search-suggestion");
        if (!options.length) return;
        if (event.key === "ArrowDown" || event.key === "ArrowUp") {
          event.preventDefault();
          highlighted = (highlighted + (event.key === "ArrowDown" ? 1 : options.length - 1)) % options.length;
          options.forEach(function (option, index) { option.classList.toggle("is-highlighted", index === highlighted); });
          input.value = options[highlighted].querySelector("span").textContent;
        } else if (event.key === "Escape") {
          closeSuggestions();
        }
      });
      input.addEventListener("blur", function () { window.setTimeout(closeSuggestions, 120); });
    });
  }

  function initMicroInteractions() {
    document.addEventListener("click", function (event) {
      var wishlist = event.target.closest(".wishlist-btn");
      if (wishlist) {
        var active = wishlist.classList.toggle("is-active");
        wishlist.setAttribute("aria-pressed", active ? "true" : "false");
      }
      var button = event.target.closest("button, .btn-shop");
      if (button) {
        button.classList.add("is-pressed");
        window.setTimeout(function () { button.classList.remove("is-pressed"); }, 180);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    highlightActiveLink();
    document.querySelectorAll(".theme-toggle").forEach(function (button) {
      button.addEventListener("click", toggleTheme);
    });
    updateThemeToggle();
    if (window.ShopCart) window.ShopCart.updateBadge();
    initScrollReveal();
    initParallax();
    initSearchSuggestions();
    initMicroInteractions();
    var yearEl = document.getElementById("footerYear");
    if (yearEl) yearEl.textContent = new Date().getFullYear();
  });
})();
