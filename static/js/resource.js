(function () {  
  var resources = {};

  var statusTone = {
    confirmed: "bg-emerald-50 text-emerald-700",
    checked_in: "bg-sky-50 text-sky-800",
    pending: "bg-slate-100 text-slate-700",
    cancelled: "bg-rose-50 text-rose-700",
    no_show: "bg-rose-50 text-rose-700",
  };

  function actionsHtml(r) {
    return (
      '<button class="rounded-md bg-amber-700 px-3 py-2 text-xs font-semibold text-white" data-edit="' + r.resourceId + '">Edit</button>' +
      '<button class="rounded-md border border-rose-300 px-3 py-2 text-xs font-semibold text-rose-700" data-delete="' + r.resourceId + '">Delete</button>'
    );
  }

  function rowHtml(r, index) {
    var sTone = statusTone[r.status] || "bg-slate-100 text-slate-700";
    return (
      "<tr>" +
      '<td class="px-4 py-4 text-slate-500">' + (index + 1) + "</td>" +
      '<td class="px-4 py-4 font-medium">' + (r.name || "—") + "</td>" +
      '<td class="px-4 py-4">' + (r.type || "—") + "</td>" +
      '<td class="px-4 py-4">' + (r.capacity != null ? r.capacity : "—") + "</td>" +
      '<td class="px-4 py-4">' + (r.location || "—") + "</td>" +
      '<td class="px-4 py-4"><span class="rounded-full ' + sTone + ' px-2.5 py-1 text-xs font-semibold">' +
        (r.status || "—").replace("_", " ") + "</span></td>" +
      '<td class="px-4 py-4">' + (r.isSpecialised ? "Required" : "Not Required") + "</td>" +
      '<td class="px-4 py-4 text-slate-500">' + (r.description || "—") + "</td>" +
      '<td class="px-4 py-4"><div class="flex flex-wrap gap-2">' + actionsHtml(r) + "</div></td>" +
      "</tr>"
    );
  }

   async function load() {
    var rows = byId("resourceRows");
    rows.innerHTML = '<tr><td colspan="9" class="px-4 py-6 text-sm text-slate-500">Loading…</td></tr>';
    try {
      var data = await api.get("/api/resource");
      resources = {};

      // API returns "resources" (plural) — confirmed from your earlier test
      var list = data.resources || [];

      if (!list.length) {
        rows.innerHTML = '<tr><td colspan="9" class="px-4 py-6 text-sm text-slate-500">No resources found.</td></tr>';
        return;
      }

      list.forEach(function (r) { resources[r.resourceId] = r; });
      rows.innerHTML = list.map(function (r, i) { return rowHtml(r, i); }).join("");

      if (typeof refreshIcons === "function") refreshIcons();

    } catch (e) {
      console.error("Failed to load resources:", e);
      rows.innerHTML = '<tr><td colspan="9" class="px-4 py-6 text-sm text-rose-500">Failed to load: ' + e.message + "</td></tr>";
    }
  }

  byId("resourceRows").addEventListener("click", function (e) {
    var ed  = e.target.closest("[data-edit]");
    var del = e.target.closest("[data-delete]");
    if (ed)  return openEdit(ed.getAttribute("data-edit"));
    if (del) return openDelete(del.getAttribute("data-delete"));
  });

  function openEdit(id) {
    var r = resources[id];
    if (!r) return;
    byId("ed_id").value          = id;
    byId("ed_name").value        = r.name        || "";
    byId("ed_type").value        = r.type        || "";
    byId("ed_capacity").value    = r.capacity    ?? "";
    byId("ed_location").value    = r.location    || "";
    byId("ed_status").value      = r.status      || "available";
    byId("ed_description").value = r.description || "";
    openModal("editResourceModal");
  }

  function openDelete(id) {
    byId("delete_id").value = id;
    openModal("deleteResourceModal");
  }
    
  byId("editResourceForm")?.addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      await api.put("/api/resource/" + byId("ed_id").value, {
        name:        byId("ed_name").value,
        type:        byId("ed_type").value,
        capacity:    Number(byId("ed_capacity").value),
        location:    byId("ed_location").value,
        status:      byId("ed_status").value,
        description: byId("ed_description").value,
      });
      closeModal("editResourceModal");
      showToast("Resource updated", "Changes have been saved.");
      load();
    } catch (err) { showToast("Could not update", err.message); }
  });

  byId("deleteConfirmBtn")?.addEventListener("click", async function () {
    try {
      await api.del("/api/resource/" + byId("delete_id").value);
      closeModal("deleteResourceModal");
      showToast("Resource deleted", "The resource has been removed.");
      load();
    } catch (err) {
      closeModal("deleteResourceModal");
      showToast("Could not delete", err.message);
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", load);
  } else {
    load();
  }
})();
