/* ============================================================
   FOODPAY / NOVURE - DASHBOARD
============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    const searchForm = document.getElementById("fpSearchForm");
    const searchButton = document.getElementById("fpSearchButton");

    if (!searchForm || !searchButton) {
        return;
    }

    searchForm.addEventListener("submit", function () {
        searchButton.classList.add("is-loading");
        searchButton.disabled = true;
    });
});
