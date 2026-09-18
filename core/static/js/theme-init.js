(function () {
  var savedTheme = localStorage.getItem("theme");
  var systemTheme = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", savedTheme || systemTheme);
})();