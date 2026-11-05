// Site behaviour. Served as a file, not inline, so a strict Content-Security-Policy
// can allow it with 'self' and no script hash is needed when it changes. Every page works
// without it: it only adds the dark-mode toggle and the home-page tag filter.
(function () {
  var toggle = document.getElementById("theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var el = document.documentElement;
      el.classList.toggle("dark");
      try {
        localStorage.setItem("theme", el.classList.contains("dark") ? "dark" : "light");
      } catch (e) {}
    });
  }

  var buttons = document.querySelectorAll(".tag-btn");
  var cards = document.querySelectorAll(".post-card");
  buttons.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var tag = btn.getAttribute("data-tag");
      buttons.forEach(function (b) {
        b.setAttribute("aria-pressed", String(b === btn));
      });
      cards.forEach(function (c) {
        var tags = (c.getAttribute("data-tags") || "").split(",");
        c.hidden = !(tag === "All" || tags.indexOf(tag) !== -1);
      });
    });
  });
})();
