
document.addEventListener("DOMContentLoaded", function () {
    loadProducts();

    let confirmBtn = document.getElementById("confirm-buy-btn");
    if (confirmBtn) {
        console.log("✅ Nút xác nhận đã được tìm thấy:", confirmBtn);
    } else {
        console.error("❌ Nút xác nhận chưa tồn tại khi DOMContentLoaded chạy!");
    }

    const modal = document.getElementById("quantity-modal");
    if (modal) {
        modal.style.display = "none"; // Ẩn modal nếu tồn tại
    } else {
        console.error("❌ Không tìm thấy phần tử #quantity-modal!");
    }
});
// Hàm tải sản phẩm và render
let allProducts = []; // Biến toàn cục để lưu trữ tất cả sản phẩm

function loadProducts() {
    fetch("/api/products/")
        .then(response => response.json())
        .then(data => {
            allProducts = data; // Lưu trữ tất cả sản phẩm để sử dụng lại
            renderProducts(allProducts); // Hiển thị tất cả sản phẩm
            loadBrandsAndCategories(data); // Tải bộ lọc sau khi có dữ liệu
        })
        .catch(error => console.error("Lỗi khi tải sản phẩm:", error));
}

// Hàm tải các bộ lọc (Hãng sản xuất, Thể loại)
function loadBrandsAndCategories(products) {
    const brands = new Set();
    const categories = new Set();

    // Duyệt qua tất cả sản phẩm để lấy các giá trị duy nhất của "thuong_hieu" và "danh_muc"
    products.forEach(product => {
        if (product.thuong_hieu) brands.add(product.thuong_hieu);
        if (product.danh_muc) categories.add(product.danh_muc);
    });

    // Cập nhật dropdown cho hãng sản xuất
    const brandSelect = document.getElementById("brand-filter");
    brandSelect.innerHTML = '<option value="">Tất cả các hãng</option>';
    brands.forEach(brand => {
        const option = document.createElement("option");
        option.value = brand;
        option.textContent = brand;
        brandSelect.appendChild(option);
    });

    // Cập nhật dropdown cho thể loại
    const categorySelect = document.getElementById("category-filter");
    categorySelect.innerHTML = '<option value="">Tất cả các thể loại</option>';
    categories.forEach(category => {
        const option = document.createElement("option");
        option.value = category;
        option.textContent = category;
        categorySelect.appendChild(option);
    });
}

// Gọi hàm khi trang đã tải xong
document.addEventListener("DOMContentLoaded", function () {
    loadProducts(); // Lần đầu tải sản phẩm và bộ lọc
});

// Hàm gọi API để tải sản phẩm và áp dụng bộ lọc
function loadFilteredProducts() {
    const searchQuery = document.getElementById("search-input").value.toLowerCase();
    const sortValue = document.getElementById("sort-filter").value;
    const brandValue = document.getElementById("brand-filter").value;
    const categoryValue = document.getElementById("category-filter").value;

    console.log("Bộ lọc giá trị: ", {searchQuery, sortValue, brandValue, categoryValue});

    // Lọc sản phẩm từ tất cả sản phẩm đã tải về
    let filteredProducts = allProducts;

    if (searchQuery) {
        filteredProducts = filteredProducts.filter(product =>
            product.ten_san_pham.toLowerCase().includes(searchQuery) ||
            product.mo_ta.toLowerCase().includes(searchQuery)
        );
    }

    if (brandValue) {
        filteredProducts = filteredProducts.filter(product => product.thuong_hieu === brandValue);
    }

    if (categoryValue) {
        filteredProducts = filteredProducts.filter(product => product.danh_muc === categoryValue);
    }

    // Sắp xếp sản phẩm nếu có
    if (sortValue === "price_asc") {
        filteredProducts.sort((a, b) => {
            const priceA = a.gia_sau_giam || a.gia;
            const priceB = b.gia_sau_giam || b.gia;
            return priceA - priceB; // Sắp xếp theo giá trị tăng dần (small to large)
        });
    } else if (sortValue === "price_desc") {
        filteredProducts.sort((a, b) => {
            const priceA = a.gia_sau_giam || a.gia;
            const priceB = b.gia_sau_giam || b.gia;
            return priceB - priceA; // Sắp xếp theo giá trị giảm dần (large to small)
        });
    } else if (sortValue === "name") {
        filteredProducts.sort((a, b) => a.ten_san_pham.localeCompare(b.ten_san_pham));
    }

    console.log("Sản phẩm sau khi lọc và sắp xếp: ", filteredProducts);

    // Hiển thị sản phẩm sau khi lọc và sắp xếp
    renderProducts(filteredProducts);
}

// Thêm các sự kiện cho các bộ lọc
document.getElementById("search-input").addEventListener("input", loadFilteredProducts);
document.getElementById("sort-filter").addEventListener("change", loadFilteredProducts);
document.getElementById("brand-filter").addEventListener("change", loadFilteredProducts);
document.getElementById("category-filter").addEventListener("change", loadFilteredProducts);

function renderProducts(products) {
    const productContainer = document.getElementById("productallall");
    productContainer.innerHTML = products.map(product => {
        const formattedOldPrice = product.gia.toLocaleString() + "đ"; // Giá gốc
        const formattedNewPrice = product.gia_sau_giam ? product.gia_sau_giam.toLocaleString() + "đ" : formattedOldPrice;

        const priceDisplay = product.gia_sau_giam 
            ? `<span class="old-price">${formattedOldPrice}</span> <span class="new-price">${formattedNewPrice}</span>`
            : `<span class="new-price">${formattedNewPrice}</span>`;

        // Kiểm tra số lượng sản phẩm
        const isOutOfStock = product.so_luong === 0;
        const buttonText = isOutOfStock ? "Hết hàng" : "Mua ngay";
        const buttonDisabled = isOutOfStock ? "disabled" : "";
        const buttonOnClick = isOutOfStock 
            ? "" 
            : `onclick="openQuantityModal(
                ${product.id}, 
                '${product.ten_san_pham.replace(/'/g, "\\'")}', 
                '${product.hinh_anh || 'images/default.png'}',
                ${product.gia},
                ${product.gia_sau_giam || product.gia},
                '${product.thuong_hieu}',
                '${product.danh_muc}'
            )"`;

        return `
        <div class="col-sm-4 product-item" 
            data-name="${product.ten_san_pham.toLowerCase()}"
            data-price="${product.gia_sau_giam || product.gia}"
            data-brand="${product.thuong_hieu}"
            data-category="${product.danh_muc}">
            
            <div class="best_shoes1">
                <p class="best_text">${product.ten_san_pham}</p>
                <div class="shoes_icon">
                    <img src="${product.hinh_anh || 'images/default.png'}" 
                         alt="${product.ten_san_pham}">
                </div>
                <div class="thuonghieu">  ${product.thuong_hieu}
                </div> 
                <div class="shoes_price">
                    ${priceDisplay}
                </div>  
            </div>
            <button class="buy-btn" ${buttonDisabled} ${buttonOnClick}>${buttonText}</button>
        </div>`;
    }).join("");
}

function openQuantityModal(productId, productName, productImg, originalPrice, discountedPrice, productBrand, productCategory) {
    console.log("🛒 Mở modal với sản phẩm:", productId, productName);

    if (!productId) {
        console.error("❌ Lỗi: productId không hợp lệ!", productId);
        return;
    }

    document.getElementById("modal-product-name").textContent = productName;
    document.getElementById("modal-product-img").src = productImg || "images/default.png";

    const priceElement = document.getElementById("modal-product-price");
    if (originalPrice !== discountedPrice) {
        priceElement.innerHTML = `<span class="old-price">${originalPrice.toLocaleString()}đ</span> <span class="new-price">${discountedPrice.toLocaleString()}đ</span>`;
    } else {
        priceElement.innerHTML = `<span class="new-price">${discountedPrice.toLocaleString()}đ</span>`;
    }

    document.getElementById("modal-product-brand").textContent = productBrand;
    document.getElementById("modal-product-category").textContent = productCategory;
    document.getElementById("modal-quantity").value = 1;
    

    const confirmButton = document.getElementById("confirm-buy-btn");
    confirmButton.setAttribute("data-product-id", productId);

    // Xóa sự kiện cũ trước khi thêm sự kiện mới
    confirmButton.removeEventListener("click", handleConfirmBuyWrapper);
    confirmButton.addEventListener("click", handleConfirmBuyWrapper);

    document.getElementById("quantity-modal").style.display = "flex";
}

// Để tránh mất event listener, tạo một hàm bọc cho handleConfirmBuy
function handleConfirmBuy(productId) {
    console.log("✅ Nút xác nhận đã được bấm!");
    
    // Kiểm tra xem người dùng đã đăng nhập chưa
    const token = localStorage.getItem("access_token");
    if (!token) {
        console.log("⚠️ Người dùng chưa đăng nhập. Hiển thị popup yêu cầu đăng nhập.");
        
        // Hiển thị popup yêu cầu đăng nhập và không gửi request đến API
        displayNotification("❌ Bạn cần đăng nhập để thực hiện thao tác này!", "error");
        showLoginPopup();  // Hiển thị popup đăng nhập
        return; // Dừng lại và không gửi request
    }

    const quantity = parseInt(document.getElementById("modal-quantity").value);

    if (quantity < 1) {
        console.log("⚠️ Số lượng không hợp lệ!");
        return;
    }

    console.log("📤 Gửi request với productId:", productId, "Số lượng:", quantity);

    fetch("/api/cart/add/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify({ san_pham_id: productId, so_luong: quantity }),
    })
    .then(response => response.json())
    .then(data => {
        console.log("✅ Phản hồi từ API:", data);

        if (data.message && data.message.includes("đã được thêm vào giỏ hàng")) {
            displayNotification("🎉 " + data.message, "success");

            closeQuantityModal(); // Đóng modal ngay khi thêm sản phẩm thành công

            updateCartUI(data); // Giả sử API trả về dữ liệu giỏ hàng
        } else {
            console.error("❌ Lỗi từ server:", data);
            displayNotification("❌ " + (data.message || "Lỗi khi thêm sản phẩm!"), "error");
        }
    })
    .catch(error => {
        console.error("❌ Lỗi khi gửi request:", error);
        displayNotification("❌ Có lỗi xảy ra, vui lòng thử lại!", "error");
    });
}

function closeQuantityModal() {
    const modal = document.getElementById("quantity-modal");
    if (modal) {
        modal.style.display = "none";
    } else {
        console.error("❌ Không tìm thấy modal để đóng!");
    }
}

function updateCartUI(cart) {
    const cartCountElement = document.getElementById("cart-count");
    const cartTotalElement = document.getElementById("cart-total");

    // Kiểm tra nếu phần tử tồn tại
    if (cartCountElement) {
        cartCountElement.textContent = cart.count; // Cập nhật số lượng sản phẩm trong giỏ hàng
    }

    if (cartTotalElement) {
        cartTotalElement.textContent = cart.total.toLocaleString() + "đ"; // Cập nhật tổng tiền
    }
}

function displayNotification(message, type) {
    console.log("📢 Hiển thị thông báo:", message, type); // Kiểm tra log

    // Tạo hoặc lấy container của thông báo
    let notificationContainer = document.getElementById('notification-container');
    if (!notificationContainer) {
        notificationContainer = document.createElement('div');
        notificationContainer.id = 'notification-container';
        document.body.appendChild(notificationContainer);
    }

    // Kiểm tra nếu đã có quá 3 thông báo trong container
    if (notificationContainer.querySelectorAll(".notification").length >= 3) {
        // Ẩn thông báo đầu tiên
        const firstNotification = notificationContainer.querySelector(".notification");
        if (firstNotification) {
            firstNotification.style.opacity = "0";
            setTimeout(() => {
                firstNotification.remove();
            }, 500); // Xóa sau khi ẩn
        }
    }

    // Tạo và thêm thông báo mới
    const notification = document.createElement("div");
    notification.classList.add("notification", type);
    notification.textContent = message;

    notificationContainer.appendChild(notification);

    // Thêm hiệu ứng mờ dần và xóa thông báo sau 2 giây
    setTimeout(() => {
        notification.style.opacity = "0";
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 2000);
}
// Hiển thị popup yêu cầu đăng nhập
function showLoginPopup() {
    // Overlay nền mờ
    const overlay = document.createElement("div");
    overlay.style.position = "fixed";
    overlay.style.top = "0";
    overlay.style.left = "0";
    overlay.style.width = "100%";
    overlay.style.height = "100%";
    overlay.style.backgroundColor = "rgba(0, 0, 0, 0.4)";
    overlay.style.zIndex = "999";

    // Popup đăng nhập
    const loginPopup = document.createElement("div");
    loginPopup.classList.add("login-popup");
    loginPopup.style.position = "fixed";
    loginPopup.style.top = "50%";
    loginPopup.style.left = "50%";
    loginPopup.style.transform = "translate(-50%, -50%)";
    loginPopup.style.padding = "20px";
    loginPopup.style.background = "white";
    loginPopup.style.borderRadius = "10px";
    loginPopup.style.boxShadow = "0 5px 15px rgba(0,0,0,0.3)";
    loginPopup.style.zIndex = "1000";
    loginPopup.innerHTML = `
        <p><strong>Bạn cần đăng nhập để thực hiện thao tác này.</strong></p>
        <button id="login-btn" style="margin-right: 10px;">Đăng nhập</button>
        <button id="cancel-btn">Hủy</button>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(loginPopup);

    // Nút "Đăng nhập"
    document.getElementById("login-btn").addEventListener("click", function () {
        console.log("Chuyển hướng đến trang đăng nhập");
        window.location.href = "/login/"; // Đưa người dùng đến trang đăng nhập
    });

    // Nút "Hủy"
    document.getElementById("cancel-btn").addEventListener("click", function () {
        console.log("Đóng popup");
        overlay.remove();
        loginPopup.remove();
    });
}
