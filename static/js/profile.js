/* Profile: load the current user and save name/email/password. */
(function () {
  async function load() {
    try {
      var data = await api.get("/api/profile");
      byId("pf_name").value = data.user.name;
      byId("pf_email").value = data.user.email;
      byId("pf_role").value = data.user.role;
    } catch (e) {}
  }

  byId("profileForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    var pw = byId("pf_password").value;
    var pw2 = byId("pf_password2").value;
    if (pw && pw !== pw2) {
      showToast("Passwords do not match", "Please re-enter your new password.");
      return;
    }
    var body = { name: byId("pf_name").value, email: byId("pf_email").value };
    if (pw) body.password = pw;
    try {
      await api.put("/api/profile", body);
      byId("pf_password").value = "";
      byId("pf_password2").value = "";
      showToast("Profile updated", "Your profile details were saved.");
    } catch (err) { showToast("Could not save", err.message); }
  });

  document.addEventListener("DOMContentLoaded", load);
})();
