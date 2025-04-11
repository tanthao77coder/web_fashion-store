 
// Hàm hiển thị thông báo dạng toast
function displayNotification(message, type = "success") {
    const container = document.getElementById("notification-container");
    if (!container) return;

    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.style.padding = "15px 25px";
    notification.style.marginBottom = "10px";
    notification.style.borderRadius = "6px";
    notification.style.fontSize = "1.1rem";
    notification.style.color = "#fff";
    notification.style.boxShadow = "0 0 15px rgba(0,0,0,0.15)";
    notification.style.opacity = "0";
    notification.style.transition = "opacity 0.5s ease";

    if (type === "success") {
      notification.style.backgroundColor = "#28a745";
    } else if (type === "error") {
      notification.style.backgroundColor = "#dc3545";
    } else {
      notification.style.backgroundColor = "#007bff";
    }

    notification.innerText = message;
    container.appendChild(notification);

    setTimeout(() => {
      notification.style.opacity = "1";
    }, 100);
    setTimeout(() => {
      notification.style.opacity = "0";
      setTimeout(() => {
        container.removeChild(notification);
      }, 500);
    }, 3000);
  }

  async function fetchCart() {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      displayNotification("Bạn cần đăng nhập để xem giỏ hàng.", "error");
      window.location.href = "{% url 'login' %}";
      return;
    }

    try {
      const response = await fetch("/api/cart/", {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Lỗi khi tải giỏ hàng.");
      }
      const cart = await response.json();
      renderCart(cart);
    } catch (error) {
      console.error("Error fetching cart:", error);
      document.getElementById("cart-container").innerHTML =
        "<p class='fs-5'>Lỗi khi tải giỏ hàng: " + error.message + "</p>";
    }
  }

  function renderCart(cart) {
    const tbody = document.getElementById("cart-items");
    tbody.innerHTML = "";

    if (!cart || !cart.items || !Array.isArray(cart.items) || cart.items.length === 0) {
        tbody.innerHTML =
            "<tr><td colspan='6' class='text-center fs-5'>Giỏ hàng của bạn đang trống.</td></tr>";
        document.getElementById("cart-summary").innerHTML = `
            <h5 class="fs-4">Tổng số lượng: <strong>0 SP</strong></h5>
            <h5 class="fs-4">Tổng tiền gốc: <span class="text-secondary">0 VND</span></h5>
            <h5 class="fs-4 text-danger">Tổng giảm giá: <span class="text-danger">-0 VND</span></h5>
            <h4 class="fs-3 fw-bold text-danger">Tổng tiền thanh toán: 0 VND</h4>
        `;
        return;
    }

    cart.items.forEach((item) => {
        const product = item.san_pham || {};
        const price = product.gia ? Number(product.gia) : 0;
        const discount = product.giam_gia ? Number(product.giam_gia) : 0;
        const discountedPrice = price - (price * discount) / 100;
        const quantity = item.so_luong || 0;
        const itemToal1= product.gia * quantity;
        const itemTotal = discountedPrice * quantity;

        const row = document.createElement("tr");
row.innerHTML = `
    <td>
        <input type="checkbox" class="select-item" data-item-id="${item.id}" 
            data-price="${itemTotal}" data-quantity="${quantity}"
            data-original-price="${price}" 
            style="transform: scale(1.3);" />
    </td>
            <td>
                <div class="d-flex align-items-center">
                    <img src="${product.hinh_anh}" alt="${product.ten_san_pham || "Sản phẩm không xác định"}"
                        style="width: 100px; height: auto; margin-right: 15px;">
                    <span>${product.ten_san_pham || "Sản phẩm không xác định"}</span>
                </div>
            </td>
            <td class="fs-5">
                ${
                  discount > 0
                    ? `<span style="text-decoration: line-through; color: gray;">${price.toLocaleString()}.đ</span>
                       <br><strong>${discountedPrice.toLocaleString()}.đ</strong>`
                    : `<strong>${price.toLocaleString()}.đ</strong>`
                }
            </td>
            <td style="display: flex; justify-content: center; height: 6em;">
                <input type="number" class="form-control quantity-input fs-5" 
                    value="${quantity}" min="1" 
                    data-item-id="${item.id}" />
            </td>
            <td class="fs-5">
              <span style="text-decoration: line-through; color: gray;">${itemToal1.toLocaleString()}.đ</span>
                <br><strong>${itemTotal.toLocaleString()}.đ</strong>
            </td>
            <td>
                <button class="btn btn-danger btn-lg" onclick="showConfirmDeleteModal(${item.id})">Xóa</button>
            </td>
        `;
        tbody.appendChild(row);

        // Gắn sự kiện tự động cập nhật số lượng khi thay đổi giá trị
        row.querySelector(".quantity-input").addEventListener("change", function () {
            updateCartItem(item.id, this.value);
        });
    });

    // Đặt tổng tiền về 0 khi mới vào trang
    document.getElementById("cart-summary").innerHTML = `
        <h5 class="fs-4">Tổng số lượng: <strong>0 Sản phẩm</strong></h5>
        <h5 class="fs-4">Tổng tiền gốc: <span class="text-secondary">0 .đ</span></h5>
        <h5 class="fs-4 text-danger">Tổng giảm giá: <span class="text-danger">-0 .đ</span></h5>
        <h4 class="fs-3 fw-bold text-danger">Tổng tiền thanh toán: 0 .đ</h4>
    `;

    // Gắn sự kiện khi tích chọn sản phẩm
    document.querySelectorAll(".select-item").forEach((checkbox) => {
        checkbox.addEventListener("change", updateTotal);
    });
}

// Hàm cập nhật tổng tiền khi checkbox thay đổi
function updateTotal() {
    let totalSelectedPrice = 0;
    let totalOriginalPrice = 0;
    let totalDiscount = 0;
    let totalSelectedQuantity = 0;

    document.querySelectorAll(".select-item:checked").forEach((checkbox) => {
        const itemPrice = Number(checkbox.getAttribute("data-price")); // Giá sau giảm giá
        const quantity = Number(checkbox.getAttribute("data-quantity"));
        const originalPrice = Number(checkbox.getAttribute("data-original-price")); // Giá gốc

        totalSelectedPrice += itemPrice;
        totalOriginalPrice += originalPrice * quantity;
        totalDiscount += (originalPrice - itemPrice / quantity) * quantity;
        totalSelectedQuantity += quantity;
    });

    document.getElementById("cart-summary").innerHTML = `
        <h5 class="fs-4">Tổng số lượng: <strong>${totalSelectedQuantity} Sản phẩm</strong></h5>
        <h5 class="fs-4">Tổng tiền gốc: <span class="text-secondary">${totalOriginalPrice.toLocaleString()}.đ</span></h5>
        <h5 class="fs-4 text-danger">Tổng giảm giá: <span class="text-danger">-${totalDiscount.toLocaleString()}.đ</span></h5>
        <h4 class="fs-3 fw-bold text-danger">Tổng tiền thanh toán: ${totalSelectedPrice.toLocaleString()}.đ</h4>
    `;
}

// Gắn sự kiện khi tích chọn sản phẩm
document.querySelectorAll(".select-item").forEach((checkbox) => {
    checkbox.addEventListener("change", updateTotal);
});


  // Hàm hiển thị modal xác nhận xóa cho 1 mục
  function showConfirmDeleteModal(itemId) {
    const modalEl = document.getElementById("confirmDeleteModal");
    const bsModal = new bootstrap.Modal(modalEl);

    // Reset sự kiện cho nút xác nhận xóa
    const confirmBtn = document.getElementById("confirmDeleteBtn");
    confirmBtn.replaceWith(confirmBtn.cloneNode(true));
    const newConfirmBtn = document.getElementById("confirmDeleteBtn");
    newConfirmBtn.addEventListener("click", function () {
      bsModal.hide();
      removeFromCart(itemId);
    });

    bsModal.show();
  }

  async function updateCartItem(itemId, newQuantity) {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      displayNotification(
        "Bạn cần đăng nhập để thực hiện hành động này.",
        "error"
      );
      return;
    }
    try {
      const response = await fetch(`/api/cart/update/${itemId}/`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ so_luong: newQuantity }),
      });
      if (response.ok) {
        displayNotification("Cập nhật số lượng thành công!", "success");
      } else {
        const errorData = await response.json();
        displayNotification(
          "Lỗi cập nhật mục " +
            itemId +
            ": " +
            (errorData.detail || JSON.stringify(errorData)),
          "error"
        );
      }
    } catch (error) {
      console.error("Error updating cart item:", error);
      displayNotification("Có lỗi xảy ra khi cập nhật mục " + itemId, "error");
    }
    fetchCart();
  }

  async function removeFromCart(cartItemId) {
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      displayNotification(
        "Bạn cần đăng nhập để thực hiện hành động này.",
        "error"
      );
      return;
    }
    try {
      const response = await fetch(`/api/cart/remove/${cartItemId}/`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (response.ok) {
        displayNotification("Mục đã được xóa khỏi giỏ hàng.", "success");
        fetchCart();
      } else {
        const errorData = await response.json();
        displayNotification(
          "Lỗi khi xóa mục: " + (errorData.detail || "Không rõ nguyên nhân"),
          "error"
        );
      }
    } catch (error) {
      console.error("Error removing cart item:", error);
      displayNotification("Có lỗi xảy ra khi xóa mục khỏi giỏ hàng.", "error");
    }
  }

  // Hàm hiển thị modal xác nhận xóa các mục đã chọn
  function showConfirmDeleteSelectedModal() {
    const modalEl = document.getElementById("confirmDeleteSelectedModal");
    const bsModal = new bootstrap.Modal(modalEl);

    // Reset sự kiện cho nút xác nhận xóa đã chọn
    const confirmSelectedBtn = document.getElementById(
      "confirmDeleteSelectedBtn"
    );
    confirmSelectedBtn.replaceWith(confirmSelectedBtn.cloneNode(true));
    const newConfirmSelectedBtn = document.getElementById(
      "confirmDeleteSelectedBtn"
    );
    newConfirmSelectedBtn.addEventListener("click", function () {
      bsModal.hide();
      deleteSelectedItems();
    });

    bsModal.show();
  }

  async function deleteSelectedItems() {
    const checkboxes = document.querySelectorAll(".select-item:checked");
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      displayNotification(
        "Bạn cần đăng nhập để thực hiện hành động này.",
        "error"
      );
      return;
    }
    for (const checkbox of checkboxes) {
      const itemId = checkbox.getAttribute("data-item-id");
      try {
        const response = await fetch(`/api/cart/remove/${itemId}/`, {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${accessToken}`,
          },
        });
        if (!response.ok) {
          const errorData = await response.json();
          displayNotification(
            "Lỗi khi xóa mục " +
              itemId +
              ": " +
              (errorData.detail || "Không rõ nguyên nhân"),
            "error"
          );
        }
      } catch (error) {
        console.error("Error deleting cart item:", error);
        displayNotification("Có lỗi xảy ra khi xóa mục " + itemId, "error");
      }
    }
    displayNotification("Đã xóa các mục đã chọn.", "success");
    fetchCart();
  }

  // Sự kiện "Select All"
  document.getElementById("select-all").addEventListener("change", function () {
    const checkboxes = document.querySelectorAll(".select-item");
    checkboxes.forEach((checkbox) => {
      checkbox.checked = this.checked;
    });
  });

  document.addEventListener("DOMContentLoaded", fetchCart);
  
  // Sự kiện nút xóa các mục đã chọn - sử dụng modal xác nhận
  document
    .getElementById("delete-selected-btn")
    .addEventListener("click", showConfirmDeleteSelectedModal);

// su kien thanh toan
document
  .getElementById("checkout-btn")
  .addEventListener("click", function () {
    const selectedItems = [];
    document.querySelectorAll(".select-item:checked").forEach((checkbox) => {
      const itemId = checkbox.getAttribute("data-item-id");
      const itemPrice = checkbox.getAttribute("data-price");
      const itemQuantity = checkbox.getAttribute("data-quantity");
      const itemOriginalPrice = checkbox.getAttribute("data-original-price");

      // Kiểm tra xem có thiếu thông tin sản phẩm không
      if (!itemId || !itemPrice || !itemQuantity || !itemOriginalPrice) {
        console.error("Dữ liệu sản phẩm không hợp lệ:", checkbox);
        displayNotification(
          "Dữ liệu sản phẩm không hợp lệ. Vui lòng kiểm tra lại.",
          "error"
        );
        return;
      }

      selectedItems.push({
        san_pham_id: itemId,
        gia_san_pham: itemPrice,
        so_luong: itemQuantity,
        gia_goc: itemOriginalPrice,
      });
    });

    if (selectedItems.length === 0) {
      displayNotification(
        "Vui lòng chọn ít nhất một sản phẩm để thanh toán.",
        "error"
      );
      return;
    }

    // Kiểm tra payload trước khi gửi yêu cầu
    console.log("Dữ liệu gửi lên: ", selectedItems);

    // Lưu danh sách sản phẩm đã chọn vào localStorage
    localStorage.setItem("selectedItems", JSON.stringify(selectedItems));

    // Chuyển hướng đến trang thanh toán
    window.location.href = `/pay/?items=${selectedItems.map(item => item.san_pham_id).join(",")}`;
  });

  document
  .getElementById("paymentForm")
  .addEventListener("submit", function (event) {
    event.preventDefault();

    // Lấy phương thức thanh toán chính (offline hoặc online)
    let selectedMethod = document.querySelector(
      "input[name='phuong_thuc_tt']:checked"
    ).value;

    let onlineMethod = document.querySelector(
      "input[name='phuong_thuc_online']:checked"
    );
    let paymentData = { phuong_thuc_tt: selectedMethod };

    if (selectedMethod === "online" && onlineMethod) {
      paymentData.phuong_thuc_online = onlineMethod.value;
    }

    // Lưu thông tin thanh toán vào localStorage
    localStorage.setItem("payment_info", JSON.stringify(paymentData));

    // Gửi form hoặc điều hướng đến trang thanh toán
    this.submit();
  });