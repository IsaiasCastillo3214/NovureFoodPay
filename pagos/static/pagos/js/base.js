/* ============================================================
   FOODPAY - BASE JS
   Menú móvil + mensajes SweetAlert
============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    const openMobileMenu = document.getElementById("fpOpenMobileMenu");
    const closeMobileMenu = document.getElementById("fpCloseMobileMenu");
    const mobileDrawer = document.getElementById("fpMobileDrawer");
    const mobileOverlay = document.getElementById("fpMobileOverlay");

    const toggleMobileUser = document.getElementById("fpToggleMobileUser");
    const mobileDropdown = document.getElementById("fpMobileDropdown");

    function abrirMenu() {
        if (!mobileDrawer || !mobileOverlay) {
            return;
        }

        mobileDrawer.classList.add("is-open");
        mobileOverlay.classList.add("is-open");
        document.body.classList.add("fp-mobile-open");
    }

    function cerrarMenu() {
        if (!mobileDrawer || !mobileOverlay) {
            return;
        }

        mobileDrawer.classList.remove("is-open");
        mobileOverlay.classList.remove("is-open");
        document.body.classList.remove("fp-mobile-open");
    }

    if (openMobileMenu) {
        openMobileMenu.addEventListener("click", abrirMenu);
    }

    if (closeMobileMenu) {
        closeMobileMenu.addEventListener("click", cerrarMenu);
    }

    if (mobileOverlay) {
        mobileOverlay.addEventListener("click", cerrarMenu);
    }

    if (toggleMobileUser && mobileDropdown) {
        toggleMobileUser.addEventListener("click", function (event) {
            event.stopPropagation();
            mobileDropdown.classList.toggle("is-open");
        });

        mobileDropdown.addEventListener("click", function (event) {
            event.stopPropagation();
        });
    }

    document.addEventListener("click", function () {
        if (mobileDropdown) {
            mobileDropdown.classList.remove("is-open");
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            cerrarMenu();

            if (mobileDropdown) {
                mobileDropdown.classList.remove("is-open");
            }
        }
    });
});

document.addEventListener("DOMContentLoaded", function () {
    const messagesContainer = document.getElementById("django-messages");

    if (!messagesContainer || !window.Swal) {
        return;
    }

    const Toast = window.Swal.mixin({
        toast: true,
        position: "bottom-end",
        showConfirmButton: false,
        timer: 5000,
        timerProgressBar: true,
        background: "#ffffff",
        color: "#0f172a",
        customClass: {
            popup: "swal-foodpay-toast"
        },
        didOpen: function (toast) {
            toast.addEventListener("mouseenter", window.Swal.stopTimer);
            toast.addEventListener("mouseleave", window.Swal.resumeTimer);
        }
    });

    const messageElements = messagesContainer.querySelectorAll(".django-message");

    messageElements.forEach(function (messageElement, index) {
        const tags = messageElement.dataset.tags || "info";
        const text = messageElement.dataset.text || "";

        let icon = "info";

        if (tags.includes("success")) {
            icon = "success";
        } else if (tags.includes("warning")) {
            icon = "warning";
        } else if (tags.includes("error")) {
            icon = "error";
        }

        setTimeout(function () {
            Toast.fire({
                icon: icon,
                title: text
            });
        }, index * 250);
    });
});