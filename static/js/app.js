/* Shared shell behaviour for signed-in pages.
 * Confirms the session (/api/user/me), drives the role-based nav, the
 * notification bell, modals, toasts and logout. Loads after api.js. */
(function () {
  var CRBS = window.CRBS || { urls: {}, activePage: "" };

  window.byId = function (id) { return document.getElementById(id); };
  window.setText = function (id, value) {
    var el = byId(id);
    if (el) el.textContent = value;
  };

  var roleLabels = {
    student: "Student",
    staff: "Staff / Faculty",
    manager: "Resource Manager",
    admin: "Admin"
  };

  window.currentRole = function () {
    return CRBS.role || localStorage.getItem("crbsRole") || "staff";
  };

  function applyRoleAccess(role, name) {
    var label = roleLabels[role] || "Staff";
    setText("headerUserName", name || label);
    setText("headerRoleBadge", label);
    setText("headerContextLabel", "MMU " + label + " Portal");

    document.querySelectorAll(".nav-btn").forEach(function (btn) {
      var roles = (btn.dataset.roles || "").split(",");
      btn.classList.toggle("hidden", roles.indexOf(role) === -1);
      btn.classList.toggle("active", btn.dataset.page === CRBS.activePage);
    });
  }

  window.toggleSidebar = function () {
    byId("sidebar").classList.toggle("hidden");
  };

  window.logout = async function () {
    try { await api.post("/api/user/logout"); } catch (e) {}
    localStorage.removeItem("crbsRole");
    localStorage.removeItem("crbsName");
    window.location.href = CRBS.urls.login;
  };

  window.openModal = function (id) { byId(id).classList.add("active"); refreshIcons(); };
  window.closeModal = function (id) { byId(id).classList.remove("active"); };

  window.showToast = function (title, message) {
    var toast = byId("toast");
    setText("toastTitle", title);
    setText("toastMessage", message || "");
    toast.classList.remove("hidden");
    window.clearTimeout(window.toastTimer);
    window.toastTimer = window.setTimeout(function () {
      toast.classList.add("hidden");
    }, 3200);
    refreshIcons();
  };

  window.refreshIcons = function () { if (window.lucide) window.lucide.createIcons(); };

  // --- Notifications bell ------------------------------------------------
  window.toggleNotifications = function () {
    var panel = byId("notifPanel");
    if (!panel) return;
    panel.classList.toggle("hidden");
    if (!panel.classList.contains("hidden")) loadNotifications();
  };

  async function loadNotifications() {
    try {
      var data = await api.get("/api/notification");
      byId("notifDot").classList.toggle("hidden", data.unread === 0);
      var list = byId("notifList");
      if (!data.notifications.length) {
        list.innerHTML = '<p class="px-4 py-6 text-center text-sm text-slate-500">No notifications.</p>';
        return;
      }
      list.innerHTML = data.notifications.map(function (n) {
        var dot = n.isRead ? "" : '<span class="mt-1 h-2 w-2 shrink-0 rounded-full bg-sky-500"></span>';
        return '<div class="flex gap-2 border-b border-slate-100 px-4 py-3">' + dot +
          '<div><p class="text-sm font-semibold text-slate-800">' + n.title + '</p>' +
          '<p class="text-xs text-slate-600">' + n.message + '</p></div></div>';
      }).join("");
    } catch (e) { /* 401 handled by api.js */ }
  }

  window.markAllRead = async function () {
    try {
      await api.post("/api/notification/read-all");
      loadNotifications();
    } catch (e) {}
  }

  async function refreshBadge() {
    try {
      var data = await api.get("/api/notification");
      var dot = byId("notifDot");
      if (dot) dot.classList.toggle("hidden", data.unread === 0);
    } catch (e) {}
  }

  // --- Session bootstrap -------------------------------------------------
  document.addEventListener("DOMContentLoaded", async function () {
    refreshIcons();

    // The server already rendered the correct role into the page (base.html),
    // so there's no flash. Still reconcile the nav/header from CRBS.role in
    // case JS-driven state (active highlight) needs it; fall back to cache.
    var bootRole = CRBS.role || localStorage.getItem("crbsRole");
    if (bootRole) applyRoleAccess(bootRole, CRBS.name || localStorage.getItem("crbsName"));

    try {
      var data = await api.get("/api/user/me");      // 401 -> redirect via api.js
      localStorage.setItem("crbsRole", data.user.role);
      localStorage.setItem("crbsName", data.user.name || "");
      applyRoleAccess(data.user.role, data.user.name);
      refreshBadge();
    } catch (e) {
      // not signed in: api.js already redirected
    }
  });
})();
