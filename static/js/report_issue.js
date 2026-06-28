/* Report Issue (US07): pick a resource from booking history, describe the
 * fault, optionally attach a photo, and notify the resource manager. */
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

  // Build the resource dropdown from the student's bookings (dedup by resource).
  async function loadResources() {
  var sel = byId("iss_resource");
  if (!sel) return; // widget not present on this page

  try {
    var data = await api.get("/api/booking");
    var bookings = (data && Array.isArray(data.bookings)) ? data.bookings : [];

    var seen = {};
    var rows = [];
    bookings.forEach(function (b) {
      if (!b.resourceId || seen[b.resourceId]) return;
      seen[b.resourceId] = true;
      rows.push({
        resourceId: b.resourceId,
        bookingId: b.bookingId,
        label: b.resourceName || ("Resource " + b.resourceId)
      });
    });

    sel.innerHTML = ""; // clear safely, no innerHTML string-building below

    var placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.textContent = rows.length ? "Select a resource…" : "No booked resources to report";
    sel.appendChild(placeholder);

    rows.forEach(function (r) {
      var opt = document.createElement("option");
      opt.value = r.resourceId;
      opt.dataset.booking = r.bookingId;
      opt.textContent = r.label; // textContent escapes automatically — no XSS vector
      sel.appendChild(opt);
    });
  } catch (e) {
    sel.innerHTML = "";
    var errOpt = document.createElement("option");
    errOpt.value = "";
    errOpt.textContent = "Could not load resources";
    sel.appendChild(errOpt);
  }
}

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

  byId("issueForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    var sel = byId("iss_resource");
    var resourceId = sel.value;
    if (!resourceId) { showToast("Select a resource", "Choose the resource you want to report."); return; }
    var description = byId("iss_description").value.trim();
    if (!description) { showToast("Description required", "Please describe the issue."); return; }

    var fd = new FormData();
    fd.append("resourceId", resourceId);
    var opt = sel.options[sel.selectedIndex];
    if (opt && opt.getAttribute("data-booking")) fd.append("bookingId", opt.getAttribute("data-booking"));
    fd.append("description", description);
    var img = byId("iss_image").files[0];
    if (img) fd.append("image", img);

    try {
      await api.postForm("/api/issue", fd);
      byId("iss_description").value = "";
      byId("iss_image").value = "";
      showToast("Issue reported", "The resource manager has been notified.");
      loadReports();
    } catch (err) { showToast("Could not submit", err.message); }
  });

  document.addEventListener("DOMContentLoaded", function () { loadResources(); loadReports(); });
})();
