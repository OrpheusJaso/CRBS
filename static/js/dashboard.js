/* Dashboard: real metrics + upcoming bookings from GET /api/dashboard.
 * Loads after app.js (byId/setText/currentRole/refreshIcons + CRBS.urls). */
(function () {
  var urls = (window.CRBS || { urls: {} }).urls;

  var profiles = {
    student: { title: "Student Booking Dashboard",
      subtitle: "Track your bookings, check-in reminders, and policy alerts.",
      primaryText: "Find Resource", primaryIcon: "search", primaryTarget: urls.search },
    staff: { title: "Staff/Faculty Dashboard",
      subtitle: "Monitor bookings, recurring sessions, and equipment requests.",
      primaryText: "New Booking", primaryIcon: "plus", primaryTarget: urls.search },
    manager: { title: "Resource Manager Dashboard",
      subtitle: "Pending approvals, resource availability and maintenance.",
      primaryText: "Review Approvals", primaryIcon: "clipboard-check", primaryTarget: urls.approvals },
    admin: { title: "Admin Control Dashboard",
      subtitle: "System approval workload and resource health.",
      primaryText: "Manage Approvals", primaryIcon: "shield-check", primaryTarget: urls.approvals }
  };

  function fmt(iso) {
    if (!iso) return "";
    var d = new Date(iso);
    return d.toLocaleString([], { day: "2-digit", month: "short",
      hour: "2-digit", minute: "2-digit" });
  }

  var statusTone = {
    confirmed: "bg-emerald-50 text-emerald-800",
    checked_in: "bg-sky-50 text-sky-800",
    pending: "bg-amber-50 text-amber-800",
    cancelled: "bg-rose-50 text-rose-700",
    no_show: "bg-rose-50 text-rose-700"
  };

  function upcomingHtml(rows) {
    if (!rows.length) {
      return '<p class="p-6 text-sm text-slate-500">No upcoming bookings.</p>';
    }
    var body = rows.map(function (b) {
      var tone = statusTone[b.status] || "bg-slate-100 text-slate-700";
      return '<div class="flex items-center justify-between gap-3 border-b border-slate-100 px-4 py-3">' +
        '<div><p class="text-sm font-semibold text-slate-800">' + (b.resourceName || "Resource") + '</p>' +
        '<p class="text-xs text-slate-500">' + fmt(b.startTime) + " – " + fmt(b.endTime) +
        (b.purpose ? " · " + b.purpose : "") + '</p></div>' +
        '<span class="rounded-full ' + tone + ' px-2.5 py-1 text-xs font-semibold">' +
        b.status.replace("_", " ") + '</span></div>';
    }).join("");
    return body;
  }

  window.handleDashboardPrimaryAction = function () {
    var target = byId("dashboardPrimaryBtn").dataset.target;
    if (target) window.location.href = target;
  };

  async function load() {
    var role = currentRole();
    var p = profiles[role] || profiles.staff;
    setText("dashboardTitle", p.title);
    setText("dashboardSubtitle", p.subtitle);
    setText("dashboardPrimaryText", p.primaryText);
    setText("dashboardMainPanelTitle", "Upcoming Bookings");
    byId("dashboardPrimaryBtn").dataset.target = p.primaryTarget;
    byId("dashboardPrimaryIconWrap").innerHTML =
      '<i data-lucide="' + p.primaryIcon + '" class="h-4 w-4"></i>';

    try {
      var data = await api.get("/api/dashboard");
      (data.metrics || []).forEach(function (m, i) {
        setText("dashMetric" + (i + 1) + "Label", m.label);
        setText("dashMetric" + (i + 1) + "Value", m.value);
      });
      byId("dashboardMainPanelContent").className = "";
      byId("dashboardMainPanelContent").innerHTML = upcomingHtml(data.upcoming || []);
      byId("dashboardSidePanel").innerHTML =
        '<div class="rounded-md border border-slate-200 bg-white p-4">' +
        '<div class="mb-2 flex items-center gap-2 font-semibold"><i data-lucide="info" class="h-4 w-4"></i> Policy</div>' +
        '<p class="text-sm text-slate-600">Bookings cannot be modified or cancelled within 24 hours of the start time. Check in to avoid no-show auto-cancel.</p></div>';
      refreshIcons();
    } catch (e) { /* 401 handled by api.js */ }
  }

  document.addEventListener("DOMContentLoaded", load);
})();
