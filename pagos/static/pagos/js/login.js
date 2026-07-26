/* ============================================================
   FOODPAY - LOGIN JS
============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("id_password");
    const togglePassword = document.getElementById("togglePassword");
    const loginForm = document.querySelector(".foodpay-login-form");
    const loginSubmit = document.getElementById("loginSubmit");

    if (passwordInput && togglePassword) {
        togglePassword.addEventListener("click", function () {
            const isPassword = passwordInput.getAttribute("type") === "password";

            passwordInput.setAttribute("type", isPassword ? "text" : "password");
            togglePassword.textContent = isPassword ? "🙈" : "👁";
            togglePassword.setAttribute(
                "aria-label",
                isPassword ? "Ocultar contraseña" : "Mostrar contraseña"
            );
        });
    }

    if (loginForm && loginSubmit) {
        loginForm.addEventListener("submit", function () {
            loginSubmit.disabled = true;
            loginSubmit.classList.add("is-loading");

            const submitText = loginSubmit.querySelector(".foodpay-login-submit-text");

            if (submitText) {
                submitText.textContent = "Ingresando...";
            }
        });
    }
});