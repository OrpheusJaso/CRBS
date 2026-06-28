/* Search & Book: live resource search + single/recurring booking modals. */
(function () {
  var current = null;  // resource chosen for the open modal

  function pad(n) { return (n < 10 ? "0" : "") + n; }
  function localValue(d) {
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate()) +
      "T" + pad(d.getHours()) + ":" + pad(d.getMinutes());
  }

  // Build a Date from the search filters (date + start time), default now.
  function chosenStart() {
    var date = byId("srch_date").value;
    var time = byId("srch_start").value || "10:00";
    if (date) return new Date(date + "T" + time);
    var d = new Date(); d.setHours(parseInt(time.slice(0, 2)), parseInt(time.slice(3)), 0, 0);
    return d;
  }

  function cardHtml(r) {
    var tone = r.available ? "bg-emerald-50 text-emerald-700" : "bg-rose-50 text-rose-700";
    var badge = r.available ? "Available" : (r.status === "available" ? "Booked" : r.status);
    var actions = r.available
      ? '<button class="rounded-md bg-sky-700 px-3 py-2 text-sm font-semibold text-white" data-book="' + r.resourceId + '">Book</button>' +
        '<button class="rounded-md border border-slate-300 px-3 py-2 text-sm font-semibold" data-recurring="' + r.resourceId + '">Recurring</button>'
      : '<span class="text-sm text-slate-500">Not available for the selected time.</span>';
    return '<article class="rounded-md border border-slate-200 bg-white p-4">' +
      '<div class="mb-3 flex items-start justify-between gap-3"><div>' +
      '<h3 class="font-semibold">' + r.name + '</h3>' +
      '<p class="text-sm text-slate-600">Capacity ' + r.capacity + ' | ' + r.location + '</p></div>' +
      '<span class="rounded-full ' + tone + ' px-2.5 py-1 text-xs font-semibold">' + badge + '</span></div>' +
      '<p class="mb-4 text-sm text-slate-700">' + (r.description || "") +
      (r.isSpecialised ? ' <span class="font-semibold text-amber-700">(approval required)</span>' : "") + '</p>' +
      '<div class="flex flex-wrap gap-2">' + actions + '</div></article>';
  }

  var byResource = {};

  function render(list) {
    byResource = {};
    var box = byId("searchResults");
    if (!list.length) { box.innerHTML = '<p class="text-sm text-slate-500">No resources match your search.</p>'; return; }
    list.forEach(function (r) { byResource[r.resourceId] = r; });
    box.innerHTML = list.map(cardHtml).join("");
    refreshIcons();
  }

  async function runSearch() {
    var params = new URLSearchParams();
    if (byId("srch_type").value) params.set("type", byId("srch_type").value);
    if (byId("srch_location").value) params.set("location", byId("srch_location").value);
    if (byId("srch_capacity").value) params.set("capacity", byId("srch_capacity").value);
    if (byId("srch_date").value) {
      params.set("date", byId("srch_date").value);
      params.set("start", byId("srch_start").value || "10:00");
    }
    try {
      var data = await api.get("/api/resource/search?" + params.toString());
      render(data.resources || []);
    } catch (e) {}
  }

  function openBooking(r) {
    current = r;
    byId("bk_resource").value = r.name;
    var start = chosenStart();
    var end = new Date(start.getTime() + 60 * 60 * 1000);
    byId("bk_start").value = localValue(start);
    byId("bk_end").value = localValue(end);
    byId("bk_capacity").value = Math.min(r.capacity || 10, 10);
    // Specialised resources need a supporting document (US04 A1).
    var docWrap = byId("bk_docWrap");
    docWrap.classList.toggle("hidden", !r.isSpecialised);
    byId("bk_document").value = "";
    openModal("bookingModal");
  }

  function openRecurring(r) {
    current = r;
    byId("rc_resource").value = r.name;
    var start = chosenStart();
    var end = new Date(start.getTime() + 60 * 60 * 1000);
    byId("rc_start").value = localValue(start);
    byId("rc_end").value = localValue(end);
    var until = new Date(start.getTime()); until.setMonth(until.getMonth() + 2);
    byId("rc_until").value = until.toISOString().slice(0, 10);
    openModal("recurringModal");
  }

  // Delegated clicks for the generated cards
  byId("searchResults").addEventListener("click", function (e) {
    var b = e.target.closest("[data-book]");
    if (b) return openBooking(byResource[b.getAttribute("data-book")]);
    var rc = e.target.closest("[data-recurring]");
    if (rc) return openRecurring(byResource[rc.getAttribute("data-recurring")]);
  });

  byId("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();
    runSearch();
  });

  byId("bookingForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      var res;
      if (current.isSpecialised) {
        var file = byId("bk_document").files[0];
        if (!file) { showToast("Document required", "Attach a supporting document for this resource."); return; }
        var fd = new FormData();
        fd.append("resourceId", current.resourceId);
        fd.append("purpose", byId("bk_purpose").value);
        fd.append("startTime", byId("bk_start").value);
        fd.append("endTime", byId("bk_end").value);
        fd.append("capacity", parseInt(byId("bk_capacity").value) || "");
        fd.append("document", file);
        res = await api.postForm("/api/booking", fd);
      } else {
        res = await api.post("/api/booking", {
          resourceId: current.resourceId,
          purpose: byId("bk_purpose").value,
          startTime: byId("bk_start").value,
          endTime: byId("bk_end").value,
          capacity: parseInt(byId("bk_capacity").value) || null
        });
      }
      closeModal("bookingModal");
      showToast(res.booking.status === "pending" ? "Approval requested" : "Booking confirmed",
                current.name + (res.booking.status === "pending" ? " awaits manager approval." : " is reserved."));
      runSearch();
    } catch (err) { showToast("Could not book", err.message); }
  });

  byId("recurringForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    try {
      var file = byId("rc_document").files[0];
      if (!file) { showToast("Document required", "Attach a supporting document for recurring bookings."); return; }
      var fd = new FormData();
      fd.append("resourceId", current.resourceId);
      fd.append("purpose", byId("rc_purpose").value);
      fd.append("recurrence", byId("rc_pattern").value);
      fd.append("startTime", byId("rc_start").value);
      fd.append("endTime", byId("rc_end").value);
      fd.append("until", byId("rc_until").value);
      fd.append("document", file);
      var res = await api.postForm("/api/booking/recurring", fd);
      closeModal("recurringModal");
      showToast("Approval requested", res.count + " sessions for " + current.name + " await manager approval.");
      runSearch();
    } catch (err) { showToast("Could not create series", err.message); }
  });

  document.addEventListener("DOMContentLoaded", runSearch);
})();
