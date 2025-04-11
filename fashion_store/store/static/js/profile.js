async function fetchOrderHistory() {
    try {
        let response = await fetch('/api/orders/');
        if (!response.ok) {
            throw new Error('Lỗi khi lấy dữ liệu đơn hàng');
        }
        let orders = await response.json();
        renderOrderHistory(orders);
    } catch (error) {
        console.error('Lỗi:', error);
    }
}

function renderOrderHistory(orders) {
    let tbody = document.querySelector("#order-history tbody");
    tbody.innerHTML = "";

    if (!orders || orders.length === 0) {
        document.getElementById("no-orders").style.display = "block";
        return;
    }

    document.getElementById("no-orders").style.display = "none";

    orders.forEach(order => {
        let tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${order.id}</td>
            <td>${new Date(order.created_at).toLocaleDateString()}</td>
            <td>${Number(order.total_price).toLocaleString()} VND</td>
            <td>${order.status}</td>
            <td><a href="/order/${order.id}/" class="btn btn-primary btn-sm">Chi tiết</a></td>
        `;
        tbody.appendChild(tr);
    });
}

document.addEventListener("DOMContentLoaded", fetchOrderHistory);
