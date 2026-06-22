/* Declarative UI actions via data-* attributes, so templates stay markup-only.
 * Uses globals from app.js (openModal/closeModal/showToast/logout) and, on the
 * dashboard, handleDashboardPrimaryAction. One element may combine attributes
 * (e.g. close a modal AND show a toast). */
(function () {
  var SEL = "[data-modal-open],[data-modal-close],[data-toast],[data-action]";

  function run(el) {
    var open = el.getAttribute("data-modal-open");
    if (open) openModal(open);

    var close = el.getAttribute("data-modal-close");
    if (close) closeModal(close);

    if (el.hasAttribute("data-toast")) {
      showToast(el.getAttribute("data-toast-title") || "Done",
                el.getAttribute("data-toast-msg") || "");
    }

    var action = el.getAttribute("data-action");
    if (action === "logout") logout();
    else if (action === "toggle-sidebar") toggleSidebar();
    else if (action === "dashboard-primary" && window.handleDashboardPrimaryAction) {
      handleDashboardPrimaryAction();
    }
  }

  document.addEventListener("click", function (e) {
    var el = e.target.closest(SEL);
    if (el && el.tagName !== "FORM") run(el);
  });

  document.addEventListener("submit", function (e) {
    if (e.target.matches(SEL)) {
      e.preventDefault();
      run(e.target);
    }
  });
})();
