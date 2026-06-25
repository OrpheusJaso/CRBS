(function () {
  async function loadResources() {
    try {
      var data = await api.get("/api/maintenance/resources");
      var sel = byId("m_name");
      if (!data.resource.length) { sel.innerHTML = '<option>No resource available</option>'; return; }
      sel.innerHTML = data.resource.map(function (r) {
        return '<option>' + r.name + '</option>';
      }).join("");
    } catch (e) {
      console.error("Failed to load resources:", e);
    }
  }

  async function loadMaintenanceResources() {
    try {
      var data = await api.get("/api/maintenance/active");
      var sel = byId("m_resource");
      if (!data.maintenance.length) { sel.innerHTML = '<option  >No resource under maintenance</option>'; return; }
      sel.innerHTML = data.maintenance.map(function (m) {
        return '<option value="' + m.maintenanceId + '">' + m.resourceName + '</option>';
      }).join("");
    } catch (e) {
      console.error("Failed to load resources:", e);
    }
  }

  byId("maintenanceForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    var body = {
      resourceName: byId("m_name").value,
      description: byId("m_description").value,
      duration: byId("m_duration").value,
    };
    if (byId("m_date").value) body.completionDate = byId("m_date").value + "T09:00";
    try {
      await api.post("/api/maintenance/create", body);
      showToast("Maintenance created!", "The resource is now under maintenance.");
    } catch (err) { showToast("Could not create maintenance: ", err.message); }
  });

  byId("completeMaintenanceForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    var maintenanceId = byId("m_resource").value;
    if (!maintenanceId) {
    showToast("Could not complete maintenance", "No resource under maintenance is selected.");
    return;
  }
    try {
      await api.post("/api/maintenance/" + maintenanceId +"/complete", {});
      showToast("Maintenance complete!", "The resource is now no longer under maintenance.");
    } catch (err) { showToast("Could not complete maintenance: ", err.message); }
  });

  document.addEventListener("DOMContentLoaded", function(){
    loadResources();
    loadMaintenanceResources();
  });
})();