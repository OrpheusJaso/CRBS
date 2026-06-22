/* Signup page: create an account (auto-logs in) then go to the dashboard. */
(function () {
  function byId(id) { return document.getElementById(id); }
  function refreshIcons() { if (window.lucide) window.lucide.createIcons(); }

  function toast(title, message) {
    var t = byId("toast");
    byId("toastTitle").textContent = title;
    byId("toastMessage").textContent = message;
    t.classList.remove("hidden");
    window.clearTimeout(window.toastTimer);
    window.toastTimer = window.setTimeout(function () { t.classList.add("hidden"); }, 4000);
    refreshIcons();
  }

  byId("signupForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      var user = await api.post("/api/user/register", {
        name: byId("name").value.trim(),
        email: byId("email").value.trim(),
        role: byId("role").value,
        password: byId("password").value
      });
      // Register logs the user in; cache role for nav, then enter the app.
      localStorage.setItem("crbsRole", user.user.role);
      window.location.href = window.CRBS.urls.dashboard;
    } catch (err) {
      toast("Could not create account", err.message);
    }
  });

  document.addEventListener("DOMContentLoaded", refreshIcons);
})();
