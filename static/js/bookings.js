/* Manage Bookings: list the user's bookings and wire check-in/modify/cancel. */
(function () {
  var bookings = {};

  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function localValue(iso) {
    var d = new Date(iso);
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
      "T" + pad(d.getHours()) + ":" + pad(d.getMinutes());
  }
  function fmt(iso) {
    var d = new Date(iso);
    return d.toLocaleString([], { day: "2-digit", month: "short", year: "numeric",
      hour: "2-digit", minute: "2-digit" });
  }

  var statusTone = {
    confirmed: "bg-emerald-50 text-emerald-700",
    checked_in: "bg-sky-50 text-sky-800",
    pending: "bg-slate-100 text-slate-700",
    cancelled: "bg-rose-50 text-rose-700",
    no_show: "bg-rose-50 text-rose-700"
  };

  function actionsHtml(b) {
    if (b.status === "confirmed") {
      return '<button class="rounded-md bg-amber-700 px-3 py-2 text-xs font-semibold text-white" data-checkin="' + b.bookingId + '">Check In</button>' +
        '<button class="rounded-md border border-slate-300 px-3 py-2 text-xs font-semibold" data-modify="' + b.bookingId + '">Modify</button>' +
        '<button class="rounded-md border border-rose-300 px-3 py-2 text-xs font-semibold text-rose-700" data-cancel="' + b.bookingId + '">Cancel</button>';
    }
    if (b.status === "pending") {
      return '<button class="rounded-md border border-slate-300 px-3 py-2 text-xs font-semibold" data-cancel="' + b.bookingId + '">Cancel</button>';
    }
    return '<span class="text-xs text-slate-400">—</span>';
  }

  function rowHtml(b) {
    var tone = statusTone[b.status] || "bg-slate-100 text-slate-700";
    return '<tr>' +
      '<td class="px-4 py-4 font-medium">' + (b.resourceName || "Resource") + '</td>' +
      '<td class="px-4 py-4">' + fmt(b.startTime) + '</td>' +
      '<td class="px-4 py-4">' + (b.purpose || "") + '</td>' +
      '<td class="px-4 py-4"><span class="rounded-full ' + tone + ' px-2.5 py-1 text-xs font-semibold">' +
      b.status.replace("_", " ") + '</span></td>' +
      '<td class="px-4 py-4"><div class="flex flex-wrap gap-2">' + actionsHtml(b) + '</div></td></tr>';
  }

  async function load() {
    try {
      var data = await api.get("/api/booking");
      bookings = {};
      var rows = byId("bookingRows");
      if (!data.bookings.length) {
        rows.innerHTML = '<tr><td colspan="5" class="px-4 py-6 text-sm text-slate-500">No bookings yet.</td></tr>';
        return;
      }
      data.bookings.forEach(function (b) { bookings[b.bookingId] = b; });
      rows.innerHTML = data.bookings.map(rowHtml).join("");
      refreshIcons();
    } catch (e) {}
  }

  async function checkIn(id) {
    try {
      await api.post("/api/booking/" + id + "/checkin");
      showToast("Checked in", "Attendance confirmed — no-show auto-cancel will not apply.");
      load();
    } catch (err) { showToast("Check-in failed", err.message); }
  }

  function openModify(id) {
    var b = bookings[id];
    byId("md_id").value = id;
    byId("md_resource").textContent = b.resourceName || "";
    byId("md_start").value = localValue(b.startTime);
    byId("md_end").value = localValue(b.endTime);
    openModal("modifyModal");
  }

  function openCancel(id) {
    byId("cancel_id").value = id;
    openModal("cancelModal");
  }

  byId("bookingRows").addEventListener("click", function (e) {
    var c = e.target.closest("[data-checkin]"); if (c) return checkIn(c.getAttribute("data-checkin"));
    var m = e.target.closest("[data-modify]"); if (m) return openModify(m.getAttribute("data-modify"));
    var x = e.target.closest("[data-cancel]"); if (x) return openCancel(x.getAttribute("data-cancel"));
  });

  byId("modifyForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      await api.put("/api/booking/" + byId("md_id").value, {
        startTime: byId("md_start").value,
        endTime: byId("md_end").value
      });
      closeModal("modifyModal");
      showToast("Booking modified", "Updated booking details were saved.");
      load();
    } catch (err) { showToast("Could not modify", err.message); }
  });

  byId("cancelConfirmBtn").addEventListener("click", async function () {
    try {
      await api.del("/api/booking/" + byId("cancel_id").value);
      closeModal("cancelModal");
      showToast("Booking cancelled", "The resource has been released for other users.");
      load();
    } catch (err) {
      closeModal("cancelModal");
      showToast("Could not cancel", err.message);
    }
  });

  document.addEventListener("DOMContentLoaded", load);
})();
