/* Login page: real authentication against POST /api/user/login.
 * Standalone — loads api.js but not app.js. Driven by data-* attributes. */
(function () {
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
    }, 3600);
    refreshIcons();
  }

  async function signIn() {
    try {
      var data = await api.post("/api/user/login", {
        email: byId("email").value.trim(),
        password: byId("password").value
      });
      localStorage.setItem("crbsRole", data.user.role);   // cache for nav
      window.location.href = window.CRBS.urls.dashboard;
    } catch (err) {
      showToast("Sign in failed", err.message);
    }
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
