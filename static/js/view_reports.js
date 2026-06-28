/* Receive Report (UR08): View Resource Reports made by Students*/

(function () {
  function fmt(iso) {
    var d = new Date(iso);
    return d.toLocaleString([], { day: "2-digit", month: "short", year: "numeric" });
  }

  var statusTone = {
    open: "bg-amber-50 text-amber-700",
    in_progress: "bg-sky-50 text-sky-800",
    resolved: "bg-emerald-50 text-emerald-700"
  };

  async function loadReports() {
    var box = byId("iss_list");
    try {
      var data = await api.get("/api/issue");
      if (!data.reports.length) {
        box.innerHTML = '<p class="text-slate-500">No issues reported yet.</p>';
        return;
      }
      box.innerHTML = data.reports.map(function (r) {
        var t = statusTone[r.status] || "bg-slate-100 text-slate-700";
        var img = r.imageUrl ? '<a href="' + r.imageUrl + '" target="_blank" class="text-xs font-semibold text-sky-700">View photo</a>' : "";
        return '<div class="rounded-md border border-slate-200 p-3">' +
          '<div class="mb-1 flex items-center justify-between gap-2">' +
          '<p class="font-medium">' + (r.resourceName || "Resource") + '</p>' +
          '<span class="rounded-full ' + t + ' px-2 py-0.5 text-xs font-semibold">' + r.status.replace("_", " ") + '</span></div>' +
          '<p class="text-xs text-slate-600">' + r.description + '</p>' +
          '<div class="mt-1 flex items-center justify-between"><span class="text-xs text-slate-400">' + fmt(r.created_at) + '</span>' + img + '</div></div>';
      }).join("");
    } catch (e) { box.innerHTML = '<p class="text-slate-500">Could not load reports.</p>'; }
  }

  document.addEventListener("DOMContentLoaded", function () {loadReports(); });
})();