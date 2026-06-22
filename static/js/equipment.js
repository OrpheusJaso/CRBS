/* Specialized Equipment: populate the catalogue and submit a request. */
(function () {
  async function loadCatalogue() {
    try {
      var data = await api.get("/api/equipment");
      var sel = byId("eq_name");
      if (!data.equipment.length) { sel.innerHTML = '<option>No equipment available</option>'; return; }
      sel.innerHTML = data.equipment.map(function (e) {
        return '<option>' + e.name + '</option>';
      }).join("");
    } catch (e) {}
  }

  byId("equipmentForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    var body = {
      equipmentName: byId("eq_name").value,
      purpose: byId("eq_purpose").value,
      attendees: parseInt(byId("eq_attendees").value) || null
    };
    if (byId("eq_date").value) body.requestedDate = byId("eq_date").value + "T09:00";
    try {
      await api.post("/api/equipment/request", body);
      showToast("Request submitted", "Your request is pending manager approval.");
    } catch (err) { showToast("Could not submit", err.message); }
  });

  document.addEventListener("DOMContentLoaded", loadCatalogue);
})();
