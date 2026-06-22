/* Login page behaviour (standalone — does not load app.js/pages.js).
 * Wired through data-* attributes so login.html stays markup-only.
 * window.CRBS.urls.dashboard is injected by the template. */
(function () {
  var CRBS = window.CRBS || { urls: {} };

  function byId(id) { return document.getElementById(id); }
  function refreshIcons() { if (window.lucide) window.lucide.createIcons(); }

  function openModal(id) {
    if (id === "forgotPasswordModal") byId("resetEmail").value = byId("email").value;
    byId(id).classList.add("active");
    refreshIcons();
  }
  function closeModal(id) { byId(id).classList.remove("active"); }

  function showToast(title, message) {
    var toast = byId("toast");
    byId("toastTitle").textContent = title;
    byId("toastMessage").textContent = message;
    toast.classList.remove("hidden");
    window.clearTimeout(window.toastTimer);
    window.toastTimer = window.setTimeout(function () {
      toast.classList.add("hidden");
    }, 3200);
    refreshIcons();
  }

  function signIn() {
    localStorage.setItem("crbsRole", byId("loginRole").value);
    window.location.href = CRBS.urls.dashboard;
  }

  function sendResetLink() {
    var email = byId("resetEmail").value;
    closeModal("forgotPasswordModal");
    showToast("Reset link sent", "A password reset link has been sent to " + email + ".");
  }

  function togglePassword() {
    var input = byId("password");
    input.type = input.type === "password" ? "text" : "password";
  }

  function handle(el) {
    var open = el.getAttribute("data-modal-open");
    if (open) openModal(open);
    var close = el.getAttribute("data-modal-close");
    if (close) closeModal(close);

    switch (el.getAttribute("data-action")) {
      case "login": signIn(); break;
      case "reset": sendResetLink(); break;
      case "toggle-password": togglePassword(); break;
    }
  }

  document.addEventListener("click", function (e) {
    var el = e.target.closest("[data-modal-open],[data-modal-close],[data-action]");
    if (el && el.tagName !== "FORM") handle(el);
  });

  document.addEventListener("submit", function (e) {
    if (e.target.matches("[data-action]")) {
      e.preventDefault();
      handle(e.target);
    }
  });

  document.addEventListener("DOMContentLoaded", refreshIcons);
})();
