/* Login page behaviour (standalone — does not load app.js).
 * window.CRBS.urls.dashboard is injected by the template. */
(function () {
  var CRBS = window.CRBS || { urls: {} };

  function byId(id) { return document.getElementById(id); }
  function refreshIcons() { if (window.lucide) window.lucide.createIcons(); }

  window.enterApp = function () {
    var role = byId("loginRole").value;
    localStorage.setItem("crbsRole", role);
    window.location.href = CRBS.urls.dashboard;
  };

  window.togglePassword = function () {
    var input = byId("password");
    input.type = input.type === "password" ? "text" : "password";
  };

  window.openModal = function (id) {
    if (id === "forgotPasswordModal") byId("resetEmail").value = byId("email").value;
    byId(id).classList.add("active");
    refreshIcons();
  };
  window.closeModal = function (id) {
    byId(id).classList.remove("active");
  };

  window.sendResetLink = function () {
    var email = byId("resetEmail").value;
    closeModal("forgotPasswordModal");
    showToast("Reset link sent", "A password reset link has been sent to " + email + ".");
  };

  window.showToast = function (title, message) {
    var toast = byId("toast");
    byId("toastTitle").textContent = title;
    byId("toastMessage").textContent = message;
    toast.classList.remove("hidden");
    window.clearTimeout(window.toastTimer);
    window.toastTimer = window.setTimeout(function () {
      toast.classList.add("hidden");
    }, 3200);
    refreshIcons();
  };

  document.addEventListener("DOMContentLoaded", refreshIcons);
})();
