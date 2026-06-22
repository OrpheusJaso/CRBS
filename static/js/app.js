/* Shared shell behaviour for every signed-in page.
 * Route URLs and the active page are injected by the template via window.CRBS
 * (so Flask's url_for stays in the HTML, not hard-coded here). */
(function () {
  var CRBS = window.CRBS || { urls: {}, activePage: "" };

  window.byId = function (id) { return document.getElementById(id); };
  window.setText = function (id, value) {
    var el = byId(id);
    if (el) el.textContent = value;
  };

  var roleProfiles = {
    student: { label: "Student", userName: "Nur Iman" },
    staff:   { label: "Staff / Faculty", userName: "Dr. Aisyah" },
    manager: { label: "Resource Manager", userName: "Mr. Daniel" },
    admin:   { label: "Admin", userName: "Admin User" }
  };

  window.currentRole = function () {
    return localStorage.getItem("crbsRole") || "staff";
  };

  function applyRoleAccess() {
    var role = currentRole();
    var profile = roleProfiles[role] || roleProfiles.staff;
    setText("headerUserName", profile.userName);
    setText("headerRoleBadge", profile.label);
    setText("headerContextLabel", "MMU " + profile.label + " Portal");

    document.querySelectorAll(".nav-btn").forEach(function (btn) {
      var roles = (btn.dataset.roles || "").split(",");
      btn.classList.toggle("hidden", roles.indexOf(role) === -1);
      btn.classList.toggle("active", btn.dataset.page === CRBS.activePage);
    });
  }

  window.toggleSidebar = function () {
    byId("sidebar").classList.toggle("hidden");
  };

  window.logout = function () {
    localStorage.removeItem("crbsRole");
    window.location.href = CRBS.urls.login;
  };

  window.openModal = function (id) {
    byId(id).classList.add("active");
    refreshIcons();
  };
  window.closeModal = function (id) {
    byId(id).classList.remove("active");
  };

  window.showToast = function (title, message) {
    var toast = byId("toast");
    setText("toastTitle", title);
    setText("toastMessage", message);
    toast.classList.remove("hidden");
    window.clearTimeout(window.toastTimer);
    window.toastTimer = window.setTimeout(function () {
      toast.classList.add("hidden");
    }, 3200);
    refreshIcons();
  };

  window.refreshIcons = function () {
    if (window.lucide) window.lucide.createIcons();
  };

  document.addEventListener("DOMContentLoaded", function () {
    applyRoleAccess();
    refreshIcons();
  });
})();
