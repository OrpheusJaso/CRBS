/* Search & Book: live resource search + single/recurring booking modals. */
(function () {
  var current = null;  // resource chosen for the open modal

  // Search & view state
  var lastResults = [];      // most recent search results
  var calDate = "";          // day the calendar view is showing (YYYY-MM-DD)
  var view = "list";         // "list" | "calendar"
  var START_HOUR = 8, END_HOUR = 20;   // calendar day window

  function pad(n) { return (n < 10 ? "0" : "") + n; }

  // Toggle the red "required field" highlight on an input/textarea.
  function setError(el, hasError) {
    el.classList.toggle("border-red-500", hasError);
    el.classList.toggle("border-slate-300", !hasError);
  }

  function todayStr() {
    var d = new Date();
    return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate());
  }
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
    var box = byId("searchResults");
    if (!list.length) { box.innerHTML = '<p class="text-sm text-slate-500">No resources match your search.</p>'; return; }
    box.innerHTML = list.map(cardHtml).join("");
    refreshIcons();
  }

  // --- Calendar view ---------------------------------------------------------

  // True if any of the resource's bookings overlaps the given hour on calDate.
  function hourBusy(bookings, hour) {
    var slotStart = new Date(calDate + "T" + pad(hour) + ":00:00");
    var slotEnd = new Date(slotStart.getTime() + 3600000);
    return (bookings || []).some(function (b) {
      var s = new Date(b.startTime), e = new Date(b.endTime);
      return s < slotEnd && e > slotStart;   // overlap
    });
  }

  function renderCalendar(list) {
    var box = byId("calendarView");
    if (!list.length) {
      box.innerHTML = '<p class="text-sm text-slate-500">No resources match your search.</p>';
      return;
    }
    var hours = [];
    for (var h = START_HOUR; h < END_HOUR; h++) hours.push(h);
    var cols = "grid-template-columns:180px repeat(" + hours.length + ",minmax(46px,1fr));";

    var header = '<div class="grid" style="' + cols + '">' +
      '<div class="px-2 py-1 text-xs font-semibold text-slate-500">Resource</div>' +
      hours.map(function (hr) {
        return '<div class="px-1 py-1 text-center text-xs font-medium text-slate-500">' + pad(hr) + ':00</div>';
      }).join("") + '</div>';

    var rows = list.map(function (r) {
      var bookable = r.status === "available";
      var cells = hours.map(function (hr) {
        if (hourBusy(r.bookings, hr))
          return '<div class="m-0.5 rounded bg-rose-100 text-center text-[9px] leading-6 text-rose-700" title="Booked — unavailable">unavailable</div>';
        if (!bookable)
          return '<div class="m-0.5 rounded bg-slate-100 text-center text-[10px] leading-6 text-slate-400" title="Unavailable">—</div>';
        return '<button type="button" class="m-0.5 rounded bg-emerald-50 text-center text-[10px] leading-6 text-emerald-700 hover:bg-emerald-100" ' +
          'data-cal-book="' + r.resourceId + '" data-hour="' + hr + '" title="Free — click to book">free</button>';
      }).join("");
      return '<div class="grid items-stretch border-t border-slate-100" style="' + cols + '">' +
        '<div class="px-2 py-2 text-sm"><p class="font-semibold">' + r.name + '</p>' +
        '<p class="text-xs text-slate-500">Cap ' + r.capacity + ' · ' + r.location + '</p></div>' +
        cells + '</div>';
    }).join("");

    box.innerHTML =
      '<div class="mb-3 flex items-center justify-between">' +
        '<p class="text-sm font-semibold">Availability for ' + calDate + '</p>' +
        '<div class="flex items-center gap-3 text-xs text-slate-500">' +
          '<span class="inline-flex items-center gap-1"><span class="h-3 w-3 rounded border border-emerald-200 bg-emerald-50"></span>Free</span>' +
          '<span class="inline-flex items-center gap-1"><span class="h-3 w-3 rounded bg-rose-100"></span>Unavailable</span>' +
        '</div></div>' +
      '<div class="min-w-[640px]">' + header + rows + '</div>';
  }

  // --- View switching --------------------------------------------------------

  function updateViewButtons() {
    [["viewListBtn", "list"], ["viewCalBtn", "calendar"]].forEach(function (p) {
      var b = byId(p[0]), active = view === p[1];
      b.classList.toggle("bg-sky-700", active);
      b.classList.toggle("text-white", active);
      b.classList.toggle("text-slate-600", !active);
    });
  }

  function renderActive() {
    var n = lastResults.length;
    byId("resultsCount").textContent = n + " resource" + (n === 1 ? "" : "s") + " found";
    if (view === "calendar") {
      byId("searchResults").classList.add("hidden");
      byId("calendarView").classList.remove("hidden");
      renderCalendar(lastResults);
    } else {
      byId("calendarView").classList.add("hidden");
      byId("searchResults").classList.remove("hidden");
      render(lastResults);
    }
    updateViewButtons();
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
      lastResults = data.resources || [];
      calDate = data.calendarDate || byId("srch_date").value || todayStr();
      byResource = {};
      lastResults.forEach(function (r) { byResource[r.resourceId] = r; });
      renderActive();
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

  // Book a specific free hour clicked in the calendar view.
  function openBookingAt(r, hour) {
    current = r;
    byId("bk_resource").value = r.name;
    var start = new Date(calDate + "T" + pad(hour) + ":00:00");
    var end = new Date(start.getTime() + 60 * 60 * 1000);
    byId("bk_start").value = localValue(start);
    byId("bk_end").value = localValue(end);
    byId("bk_capacity").value = Math.min(r.capacity || 10, 10);
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

  // Book a free slot from the calendar view.
  byId("calendarView").addEventListener("click", function (e) {
    var c = e.target.closest("[data-cal-book]");
    if (!c) return;
    var r = byResource[c.getAttribute("data-cal-book")];
    if (r) openBookingAt(r, parseInt(c.getAttribute("data-hour"), 10));
  });

  // List / Calendar view toggle — re-renders the current results, no refetch.
  byId("viewListBtn").addEventListener("click", function () { view = "list"; renderActive(); });
  byId("viewCalBtn").addEventListener("click", function () { view = "calendar"; renderActive(); });

  byId("searchForm").addEventListener("submit", function (e) {
    e.preventDefault();
    runSearch();
  });

  byId("bookingForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    // Purpose and Attendees are required — highlight whichever is blank.
    var purposeEl = byId("bk_purpose"), attendeesEl = byId("bk_capacity");
    var attendees = parseInt(attendeesEl.value, 10);
    var purposeMissing = !purposeEl.value.trim();
    var attendeesMissing = !attendeesEl.value.trim() || isNaN(attendees) || attendees < 1;
    setError(purposeEl, purposeMissing);
    setError(attendeesEl, attendeesMissing);
    if (purposeMissing || attendeesMissing) {
      showToast("Missing information", "Please enter a purpose and the number of attendees.");
      (purposeMissing ? purposeEl : attendeesEl).focus();
      return;
    }

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

  // Clear the required-field highlight once the user starts fixing it.
  byId("bk_purpose").addEventListener("input", function () { setError(byId("bk_purpose"), false); });
  byId("bk_capacity").addEventListener("input", function () { setError(byId("bk_capacity"), false); });

  document.addEventListener("DOMContentLoaded", runSearch);
})();
