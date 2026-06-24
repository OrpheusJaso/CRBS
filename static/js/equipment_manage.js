(function () {  
  var equipment = {};

  var conditionTone = {
    good:   "bg-emerald-50 text-emerald-700",
    degraded:    "bg-amber-50 text-amber-700",
    faulty: "bg-orange-50 text-orange-700",
    broken: "bg-rose-50 text-rose-700",
  };

  function actionsHtml(eq) {
    return (
      '<button class="rounded-md bg-amber-700 px-3 py-2 text-xs font-semibold text-white" data-edit="' + eq.equipmentId + '">Edit</button>' +
      '<button class="rounded-md border border-rose-300 px-3 py-2 text-xs font-semibold text-rose-700" data-delete="' + eq.equipmentId + '">Delete</button>'
    );
  }

  function rowHtml(eq) {
    var cTone = conditionTone[eq.condition] || "bg-slate-100 text-slate-700";
    return (
      "<tr>" +
      '<td class="px-4 py-4 text-slate-500">' + (eq.equipmentId) + "</td>" +
      '<td class="px-4 py-4 font-medium">' + (eq.name || "—") + "</td>" +
      '<td class="px-4 py-4 text-slate-500">' + (eq.resourceId) + "</td>" +
      '<td class="px-4 py-4">' + (eq.type || "—") + "</td>" +
      '<td class="px-4 py-4">' + (eq.quantity != null ? eq.quantity : "—") + "</td>" +
      '<td class="px-4 py-4">' + (eq.isSpecialised ? "Yes" : "No") + "</td>" +
      '<td class="px-4 py-4"><span class="rounded-full ' + cTone + ' px-2.5 py-1 text-xs font-semibold">' +
        (eq.condition || "—").replace("_", " ") + "</span></td>" +
      '<td class="px-4 py-4"><div class="flex flex-wrap gap-2">' + actionsHtml(eq) + "</div></td>" +
      "</tr>"
    );
  }

   async function load() {
    var rows = byId("equipmentRows");
    rows.innerHTML = '<tr><td colspan="8" class="px-4 py-6 text-sm text-slate-500">Loading…</td></tr>';
    try {
      var data = await api.get("/api/equipment/manage");
      equipment = {};

      var list = data.equipment || [];

      if (!list.length) {
        rows.innerHTML = '<tr><td colspan="8" class="px-4 py-6 text-sm text-slate-500">No Equipment found.</td></tr>';
        return;
      }

      list.forEach(function (eq) { equipment[eq.equipmentId] = eq; });
      rows.innerHTML = list.map(function (eq, i) { return rowHtml(eq, i); }).join("");

      if (typeof refreshIcons === "function") refreshIcons();

    } catch (e) {
      console.error("Failed to load resources:", e);
      rows.innerHTML = '<tr><td colspan="8" class="px-4 py-6 text-sm text-rose-500">Failed to load: ' + e.message + "</td></tr>";
    }
  }

  byId("equipmentRows").addEventListener("click", function (e) {
    var ed  = e.target.closest("[data-edit]");
    var del = e.target.closest("[data-delete]");
    if (ed)  return openEdit(ed.getAttribute("data-edit"));
    if (del) return openDelete(del.getAttribute("data-delete"));
  });

  function openEdit(id) {
    var eq = equipment[id];
    if (!eq) return;
    byId("ed_id").value          = id;
    byId("ed_resourceId").value  = eq.resourceId  || "";
    byId("ed_name").value        = eq.name        || "";
    byId("ed_type").value        = eq.type        || "";
    byId("ed_quantity").value    = eq.quantity    ?? "";
    byId("ed_specialised").checked = !!eq.isSpecialised;
    byId("ed_condition").value   = eq.condition    || "good";
    openModal("modifyEquipmentModal");
  }

  function openDelete(id) {
    byId("delete_equipment_id").value = id;
    openModal("deleteEquipmentModal");
  }
    
  byId("createEquipmentForm")?.addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      await api.post("/api/equipment/manage", {
        name:           byId("eq_name").value.trim(),
        resourceId:     Number(byId("eq_resourceId").value),
        type:           byId("eq_type").value.trim(),
        quantity:       Number(byId("eq_quantity").value),
        condition:      byId("eq_condition").value,
        isSpecialised:  byId("eq_specialised").checked,
      });
      closeModal("createEquipmentModal");
      showToast("Success", "Equipment have been created.");  
      byId("createEquipmentForm").reset();
      load();
    } catch (err) { showToast("Unable to create equipment: ", err.message); }
  });

  byId("modifyEquipmentForm")?.addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      await api.put("/api/equipment/manage/" + byId("ed_id").value, {
        name:           byId("ed_name").value.trim(),
        resourceId:     Number(byId("ed_resourceId").value),
        type:           byId("ed_type").value.trim(),
        quantity:       Number(byId("ed_quantity").value),
        condition:      byId("ed_condition").value,
        isSpecialised:  byId("ed_specialised").checked,
      });
      closeModal("modifyEquipmentModal");
      showToast("Equipment updated", "Changes have been saved.");
      load();
    } catch (err) { showToast("Could not update", err.message); }
  });

  byId("deleteConfirmationBtn")?.addEventListener("click", async function () {
    try {
      await api.del("/api/equipment/manage/" + byId("delete_equipment_id").value);
      closeModal("deleteEquipmentModal");
      showToast("Equipment deleted", "The equipment has been removed.");
      load();
    } catch (err) {
      closeModal("deleteEquipmentModal");
      showToast("Could not delete", err.message);
    }
  });

  document.addEventListener("DOMContentLoaded", load);
})();
