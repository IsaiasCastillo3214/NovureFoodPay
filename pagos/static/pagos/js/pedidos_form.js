/* ============================================================
   FOODPAY / NOVURE - FORMULARIO DE PEDIDOS
============================================================ */

document.addEventListener("DOMContentLoaded", function () {
    const orderForm = document.querySelector("[data-product-search-url]");
    const productsContainer = document.getElementById("products-container");
    const addProductButton = document.getElementById("add-product");
    const totalPedido = document.getElementById("total-pedido");

    const tipoEntrega = document.getElementById("id_tipo_entrega");
    const datosClienteSection = document.getElementById("datos-cliente-section");

    const nombreCliente = document.getElementById("id_nombre_cliente");
    const telefonoCliente = document.getElementById("id_telefono_cliente");
    const detalleEntrega = document.getElementById("id_detalle_entrega");

    if (!orderForm || !productsContainer || !totalPedido) {
        return;
    }

    const productSearchUrl = orderForm.dataset.productSearchUrl;

    let ultimoNombreCliente = "";
    let ultimoTelefonoCliente = "";
    let ultimoDetalleEntrega = "";

    function formatearPrecio(valor) {
        return "$" + Number(valor || 0).toLocaleString("es-CL");
    }

    function debounce(callback, delay) {
        let timeoutId;

        return function (...args) {
            clearTimeout(timeoutId);

            timeoutId = setTimeout(function () {
                callback.apply(null, args);
            }, delay);
        };
    }

    function actualizarFila(row) {
        const inputProductoId = row.querySelector(".product-id-input");
        const cantidadInput = row.querySelector(".quantity-input");
        const subtotalText = row.querySelector(".line-total strong");

        if (!inputProductoId || !cantidadInput || !subtotalText) {
            return;
        }

        const precio = Number(inputProductoId.dataset.price || 0);
        const cantidad = parseInt(cantidadInput.value) || 0;
        const subtotal = precio * cantidad;

        subtotalText.textContent = formatearPrecio(subtotal);

        actualizarTotal();
    }

    function actualizarTotal() {
        let total = 0;

        const rows = productsContainer.querySelectorAll(".product-row");

        rows.forEach(function (row) {
            const inputProductoId = row.querySelector(".product-id-input");
            const cantidadInput = row.querySelector(".quantity-input");

            if (!inputProductoId || !cantidadInput) {
                return;
            }

            const precio = Number(inputProductoId.dataset.price || 0);
            const cantidad = parseInt(cantidadInput.value) || 0;

            if (inputProductoId.value) {
                total += precio * cantidad;
            }
        });

        totalPedido.textContent = formatearPrecio(total);
    }

    function cerrarResultados(row) {
        const resultsBox = row.querySelector(".product-search-results");

        if (!resultsBox) {
            return;
        }

        resultsBox.classList.remove("is-open");
        resultsBox.innerHTML = "";
    }

    function renderizarResultados(row, productos) {
        const resultsBox = row.querySelector(".product-search-results");

        if (!resultsBox) {
            return;
        }

        resultsBox.innerHTML = "";

        if (!productos.length) {
            resultsBox.innerHTML = `
                <div class="product-search-empty">
                    Sin resultados
                </div>
            `;

            resultsBox.classList.add("is-open");
            return;
        }

        productos.forEach(function (producto) {
            const item = document.createElement("button");

            item.type = "button";
            item.className = "product-search-item";

            item.innerHTML = `
                <span>${producto.nombre}</span>
                <strong>${formatearPrecio(producto.precio)}</strong>
            `;

            item.addEventListener("click", function () {
                seleccionarProducto(row, producto);
            });

            resultsBox.appendChild(item);
        });

        resultsBox.classList.add("is-open");
    }

    function buscarProductos(row, texto) {
        const resultsBox = row.querySelector(".product-search-results");

        if (!resultsBox || !productSearchUrl) {
            return;
        }

        if (!texto || texto.trim().length < 1) {
            cerrarResultados(row);
            return;
        }

        resultsBox.innerHTML = `
            <div class="product-search-empty">
                Buscando...
            </div>
        `;

        resultsBox.classList.add("is-open");

        fetch(productSearchUrl + "?q=" + encodeURIComponent(texto))
            .then(function (response) {
                if (!response.ok) {
                    throw new Error("Error en la búsqueda de productos.");
                }

                return response.json();
            })
            .then(function (data) {
                renderizarResultados(row, data.productos || []);
            })
            .catch(function () {
                resultsBox.innerHTML = `
                    <div class="product-search-empty">
                        Error al buscar productos
                    </div>
                `;

                resultsBox.classList.add("is-open");
            });
    }

    function seleccionarProducto(row, producto) {
        const inputTexto = row.querySelector(".product-search-input");
        const inputProductoId = row.querySelector(".product-id-input");

        if (!inputTexto || !inputProductoId) {
            return;
        }

        inputTexto.value = producto.nombre + " - " + formatearPrecio(producto.precio);
        inputProductoId.value = producto.id;
        inputProductoId.dataset.price = producto.precio;

        cerrarResultados(row);
        actualizarFila(row);
    }

    function inicializarFila(row) {
        const inputTexto = row.querySelector(".product-search-input");
        const inputProductoId = row.querySelector(".product-id-input");
        const cantidadInput = row.querySelector(".quantity-input");
        const removeButton = row.querySelector(".remove-product");

        if (!inputTexto || !inputProductoId || !cantidadInput || !removeButton) {
            return;
        }

        const buscarProductosDebounced = debounce(function () {
            buscarProductos(row, inputTexto.value);
        }, 250);

        inputTexto.addEventListener("input", function () {
            inputProductoId.value = "";
            inputProductoId.dataset.price = "0";

            actualizarFila(row);
            buscarProductosDebounced();
        });

        inputTexto.addEventListener("focus", function () {
            if (inputTexto.value.trim().length > 0 && !inputProductoId.value) {
                buscarProductos(row, inputTexto.value);
            }
        });

        inputTexto.addEventListener("keydown", function (event) {
            if (event.key === "Escape") {
                cerrarResultados(row);
            }
        });

        cantidadInput.addEventListener("input", function () {
            if (parseInt(cantidadInput.value) < 1) {
                cantidadInput.value = 1;
            }

            actualizarFila(row);
        });

        removeButton.addEventListener("click", function () {
            const filas = productsContainer.querySelectorAll(".product-row");

            if (filas.length === 1) {
                inputTexto.value = "";
                inputProductoId.value = "";
                inputProductoId.dataset.price = "0";
                cantidadInput.value = 1;

                cerrarResultados(row);
                actualizarFila(row);
                return;
            }

            row.remove();
            actualizarTotal();
        });

        actualizarFila(row);
    }

    function agregarFilaProducto() {
        const primeraFila = productsContainer.querySelector(".product-row");

        if (!primeraFila) {
            return;
        }

        const nuevaFila = primeraFila.cloneNode(true);

        const inputTexto = nuevaFila.querySelector(".product-search-input");
        const inputProductoId = nuevaFila.querySelector(".product-id-input");
        const cantidadInput = nuevaFila.querySelector(".quantity-input");
        const subtotalText = nuevaFila.querySelector(".line-total strong");
        const resultsBox = nuevaFila.querySelector(".product-search-results");

        if (!inputTexto || !inputProductoId || !cantidadInput || !subtotalText || !resultsBox) {
            return;
        }

        inputTexto.value = "";
        inputProductoId.value = "";
        inputProductoId.dataset.price = "0";
        cantidadInput.value = 1;
        subtotalText.textContent = "$0";
        resultsBox.innerHTML = "";
        resultsBox.classList.remove("is-open");

        productsContainer.appendChild(nuevaFila);

        inicializarFila(nuevaFila);
        actualizarTotal();

        inputTexto.focus();
    }

    function controlarTipoEntrega() {
        if (!tipoEntrega || !datosClienteSection) {
            return;
        }

        if (tipoEntrega.value === "retiro_tienda") {
            if (nombreCliente && nombreCliente.value !== "Cliente en local") {
                ultimoNombreCliente = nombreCliente.value;
            }

            if (telefonoCliente && telefonoCliente.value !== "00000000") {
                ultimoTelefonoCliente = telefonoCliente.value;
            }

            if (detalleEntrega && detalleEntrega.value !== "Retiro en tienda") {
                ultimoDetalleEntrega = detalleEntrega.value;
            }

            datosClienteSection.style.display = "none";

            if (nombreCliente) {
                nombreCliente.value = "Cliente en local";
            }

            if (telefonoCliente) {
                telefonoCliente.value = "00000000";
            }

            if (detalleEntrega) {
                detalleEntrega.value = "Retiro en tienda";
            }

            return;
        }

        datosClienteSection.style.display = "block";

        if (nombreCliente && nombreCliente.value === "Cliente en local") {
            nombreCliente.value = ultimoNombreCliente;
        }

        if (telefonoCliente && telefonoCliente.value === "00000000") {
            telefonoCliente.value = ultimoTelefonoCliente;
        }

        if (detalleEntrega && detalleEntrega.value === "Retiro en tienda") {
            detalleEntrega.value = ultimoDetalleEntrega;
        }
    }

    productsContainer.querySelectorAll(".product-row").forEach(function (row) {
        inicializarFila(row);
    });

    if (addProductButton) {
        addProductButton.addEventListener("click", function () {
            agregarFilaProducto();
        });
    }

    if (tipoEntrega) {
        tipoEntrega.addEventListener("change", controlarTipoEntrega);
        controlarTipoEntrega();
    }

    document.addEventListener("click", function (event) {
        const clickedInsideCombobox = event.target.closest(".product-ajax-combobox");

        if (!clickedInsideCombobox) {
            productsContainer.querySelectorAll(".product-row").forEach(function (row) {
                cerrarResultados(row);
            });
        }
    });

    actualizarTotal();
});
