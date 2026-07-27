/* ============================================================
   FOODPAY / NOVURE - BASE JS
============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    initMobileNavbar();
    initDjangoMessages();
});

/* ============================================================
   NAVBAR MÓVIL
============================================================ */

function initMobileNavbar() {
    const body = document.body;

    const openMenuButton = document.getElementById("fpOpenMobileMenu");
    const closeMenuButton = document.getElementById("fpCloseMobileMenu");
    const mobileDrawer = document.getElementById("fpMobileDrawer");
    const mobileOverlay = document.getElementById("fpMobileOverlay");

    const toggleUserButton = document.getElementById("fpToggleMobileUser");
    const mobileDropdown = document.getElementById("fpMobileDropdown");

    function openDrawer() {
        if (!mobileDrawer || !mobileOverlay) {
            return;
        }

        mobileDrawer.classList.add("is-open");
        mobileOverlay.classList.add("is-open");
        body.classList.add("fp-mobile-menu-open");
    }

    function closeDrawer() {
        if (!mobileDrawer || !mobileOverlay) {
            return;
        }

        mobileDrawer.classList.remove("is-open");
        mobileOverlay.classList.remove("is-open");
        body.classList.remove("fp-mobile-menu-open");
    }

    function toggleDropdown() {
        if (!mobileDropdown) {
            return;
        }

        mobileDropdown.classList.toggle("is-open");
    }

    function closeDropdown() {
        if (!mobileDropdown) {
            return;
        }

        mobileDropdown.classList.remove("is-open");
    }

    if (openMenuButton) {
        openMenuButton.addEventListener("click", openDrawer);
    }

    if (closeMenuButton) {
        closeMenuButton.addEventListener("click", closeDrawer);
    }

    if (mobileOverlay) {
        mobileOverlay.addEventListener("click", closeDrawer);
    }

    if (toggleUserButton) {
        toggleUserButton.addEventListener("click", function (event) {
            event.stopPropagation();
            toggleDropdown();
        });
    }

    document.addEventListener("click", function (event) {
        const clickedInsideDropdown = event.target.closest("#fpMobileDropdown");
        const clickedUserButton = event.target.closest("#fpToggleMobileUser");

        if (!clickedInsideDropdown && !clickedUserButton) {
            closeDropdown();
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            closeDrawer();
            closeDropdown();
        }
    });
}

/* ============================================================
   MENSAJES DJANGO RESPONSIVE
============================================================ */

function initDjangoMessages() {
    const messagesContainer = document.getElementById("django-messages");

    if (!messagesContainer || typeof Swal === "undefined") {
        return;
    }

    const messages = messagesContainer.querySelectorAll(".django-message");

    if (!messages.length) {
        return;
    }

    messages.forEach(function (message, index) {
        const tags = message.dataset.tags || "info";
        const text = message.dataset.text || "";

        setTimeout(function () {
            showFoodPayAlert(tags, text);
        }, index * 350);
    });
}

function showFoodPayAlert(tags, text) {
    const alertConfig = getAlertConfig(tags);
    const isMobile = window.innerWidth <= 600;

    if (isMobile) {
        Swal.fire({
            toast: false,
            icon: alertConfig.icon,
            title: text,

            position: "top",
            width: "calc(100vw - 24px)",

            showConfirmButton: false,
            timer: 4300,
            timerProgressBar: true,

            backdrop: false,
            allowOutsideClick: true,
            allowEscapeKey: true,

            customClass: {
                popup: "foodpay-mobile-alert-popup",
                title: "foodpay-mobile-alert-title",
            },
        });

        return;
    }

    Swal.fire({
        toast: true,
        icon: alertConfig.icon,
        title: text,

        position: "top-end",
        width: 390,

        showConfirmButton: false,
        timer: 4300,
        timerProgressBar: true,

        customClass: {
            popup: "foodpay-toast-popup",
            title: "foodpay-toast-title",
        },
    });
}

function getAlertConfig(tags) {
    if (tags.includes("success")) {
        return {
            icon: "success",
        };
    }

    if (tags.includes("error") || tags.includes("danger")) {
        return {
            icon: "error",
        };
    }

    if (tags.includes("warning")) {
        return {
            icon: "warning",
        };
    }

    return {
        icon: "info",
    };
}