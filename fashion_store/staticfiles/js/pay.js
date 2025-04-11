document.addEventListener("DOMContentLoaded", function () {
    const confirmBtn = document.getElementById("confirmPayment");
    const paymentForm = document.getElementById("paymentForm");
    const csrfTokenElement = document.querySelector("input[name='csrfmiddlewaretoken']");
    
    if (!csrfTokenElement) {
        alert("Lỗi hệ thống: Không tìm thấy CSRF token!");
        return;
    }
    const csrfToken = csrfTokenElement.value;

    async function getAuthToken() {
        return localStorage.getItem("access_token");
    }

    async function refreshAuthToken() {
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) return null;
        
        const response = await fetch("/api/auth/refresh/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh: refreshToken })
        });
        
        if (response.ok) {
            const newTokens = await response.json();
            localStorage.setItem("access_token", newTokens.access);
            return newTokens.access;
        }
        return null;
    }

    async function fetchWithAuth(url, options = {}) {
        let authToken = await getAuthToken();
        
        options.headers = {
            ...(options.headers || {}),
            "Authorization": `Bearer ${authToken}`,
            "X-CSRFToken": csrfToken
        };
        
        let response = await fetch(url, options);
        
        if (response.status === 401) {
            authToken = await refreshAuthToken();
            if (!authToken) {
                alert("Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại!");
                window.location.href = "/login/";
                return;
            }
            options.headers["Authorization"] = `Bearer ${authToken}`;
            response = await fetch(url, options);
        }
        return response;
    }

    async function createOrder(selectedItems, paymentMethod, onlineMethod) {
        try {
            const response = await fetchWithAuth("/api/orders/create/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    cart_items: selectedItems,
                    phuong_thuc_tt: paymentMethod,
                    phuong_thuc_online: onlineMethod
                })
            });

            const data = await response.json();
            if (response.ok) {
                return data.order_id; // Trả về ID của đơn hàng mới tạo
            } else {
                alert(data.error || "Đặt hàng thất bại!");
                return null;
            }
        } catch (error) {
            console.error("Lỗi khi tạo đơn hàng:", error);
            alert("Có lỗi xảy ra khi tạo đơn hàng, vui lòng thử lại!");
            return null;
        }
    }

    async function processPayment(orderId, paymentMethod, onlineMethod) {
        try {
            const response = await fetchWithAuth("/api/orders/payment/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    don_hang_ids: [orderId],
                    phuong_thuc_tt: paymentMethod,
                    cong_thanh_toan: onlineMethod
                })
            });

            const result = await response.json();
            if (response.ok) {
                alert("Thanh toán thành công!");
                window.location.href = "/profile/";
            } else {
                alert("Lỗi: " + (result.error || "Có lỗi xảy ra!"));
            }
        } catch (error) {
            console.error("Lỗi khi thanh toán:", error);
            alert("Có lỗi xảy ra, vui lòng thử lại!");
        }
    }

    confirmBtn.addEventListener("click", async function (event) {
        event.preventDefault();

        const authToken = await getAuthToken();
        if (!authToken) {
            alert("Bạn chưa đăng nhập. Vui lòng đăng nhập để tiếp tục.");
            window.location.href = "/login/";
            return;
        }

        const selectedMethod = document.querySelector("input[name='phuong_thuc_tt']:checked")?.value;
        const onlineMethod = document.querySelector("input[name='phuong_thuc_online']:checked")?.value || null;
        const selectedItems = Array.from(document.querySelectorAll("tbody tr"), row => ({
            san_pham_id: row.dataset.id,
            so_luong: row.dataset.quantity
        }));

        if (!selectedMethod || selectedItems.length === 0) {
            alert("Vui lòng chọn phương thức thanh toán và ít nhất một sản phẩm!");
            return;
        }
        if (selectedMethod === "online" && !onlineMethod) {
            alert("Vui lòng chọn cổng thanh toán!");
            return;
        }

        confirmBtn.disabled = true;
        confirmBtn.innerText = "Đang xử lý...";

        try {
            // 🛒 **BƯỚC 1: Tạo đơn hàng**
            const orderId = await createOrder(selectedItems, selectedMethod, onlineMethod);
            if (!orderId) {
                confirmBtn.disabled = false;
                confirmBtn.innerText = "✅ Thanh toán";
                return;
            }

            // 💳 **BƯỚC 2: Thanh toán đơn hàng vừa tạo**
            await processPayment(orderId, selectedMethod, onlineMethod);
        } finally {
            confirmBtn.disabled = false;
            confirmBtn.innerText = "✅ Thanh toán";
        }
    });

});
