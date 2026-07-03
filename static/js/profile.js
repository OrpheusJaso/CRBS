/* Profile: load the current user, show booking history, save name/email/password. */
(function () {
  function fmt(iso) {
    var d = new Date(iso);
    return d.toLocaleString([], { day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit" });
  }

  var tone = {
    confirmed: "bg-emerald-50 text-emerald-700",
    checked_in: "bg-sky-50 text-sky-800",
    pending: "bg-amber-50 text-amber-700",
    cancelled: "bg-rose-50 text-rose-700",
    no_show: "bg-rose-50 text-rose-700"
  };

  async function load() {
    try {
      var data = await api.get("/api/profile");
      byId("pf_name").value = data.user.name;
      byId("pf_email").value = data.user.email;
      byId("pf_role").value = data.user.role;
    } catch (e) {}
  }

  async function loadHistory() {
    var box = byId("pf_history");
    try {
      var data = await api.get("/api/booking");
      if (!data.bookings.length) {
        box.innerHTML = '<p class="text-slate-500">No bookings yet.</p>';
        return;
      }
      box.innerHTML = data.bookings.map(function (b) {
        var t = tone[b.status] || "bg-slate-100 text-slate-700";
        return '<div class="flex items-center justify-between gap-2 rounded-md border border-slate-200 px-3 py-2">' +
          '<div><p class="font-medium">' + (b.resourceName || "Resource") + '</p>' +
          '<p class="text-xs text-slate-500">' + fmt(b.startTime) + '</p></div>' +
          '<span class="rounded-full ' + t + ' px-2 py-0.5 text-xs font-semibold">' +
          b.status.replace("_", " ") + '</span></div>';
      }).join("");
    } catch (e) { box.innerHTML = '<p class="text-slate-500">Could not load history.</p>'; }
  }

  byId("profileForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    var pw = byId("pf_password").value;
    var pw2 = byId("pf_password2").value;
    if (pw && pw !== pw2) {
      showToast("Passwords do not match", "Please re-enter your new password.");
      return;
    }
    if (pw && !byId("pf_current").value) {
      showToast("Current password required", "Enter your current password to change it.");
      return;
    }
    var body = { name: byId("pf_name").value, email: byId("pf_email").value };
    if (pw) { body.password = pw; body.currentPassword = byId("pf_current").value; }
    try {
      var res = await api.put("/api/profile", body);
      // Reflect the saved values immediately so no page refresh is needed:
      // update the form fields, the header name, and the cached name.
      if (res && res.user) {
        byId("pf_name").value = res.user.name;
        byId("pf_email").value = res.user.email;
        localStorage.setItem("crbsName", res.user.name || "");
        var hdr = byId("headerUserName");
        if (hdr) hdr.textContent = res.user.name || "";
      }
      byId("pf_current").value = "";
      byId("pf_password").value = "";
      byId("pf_password2").value = "";
      showToast("Profile updated", "Your profile details were saved.");
    } catch (err) { showToast("Could not save", err.message); }
  });

  document.addEventListener("DOMContentLoaded", function () { load(); loadHistory(); });
})();
