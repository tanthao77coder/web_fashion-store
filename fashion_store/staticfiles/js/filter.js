let allProducts = []; // Lưu danh sách sản phẩm để lọc mà không cần gọi API lại

async function fetchProducts() {
    try {
        const response = await fetch("/api/products/");
        allProducts = await response.json();

        renderProducts(allProducts);
        loadFilterOptions(allProducts);

        // Sau khi tải sản phẩm, áp dụng bộ lọc nếu đã có giá trị trước đó
        applyFilters();
    } catch (error) {
        console.error("Lỗi khi tải sản phẩm:", error);
    }
}
function renderProducts(products) {
    console.log("Sản phẩm sau khi lọc:", products); // Kiểm tra danh sách sản phẩm
    const productList = document.getElementById("product-list");
    productList.innerHTML = "";

    if (products.length === 0) {
        productList.innerHTML = `<p class="text-center text-danger">Không tìm thấy sản phẩm phù hợp.</p>`;
        return;
    }

    products.forEach((product) => {
        // Kiểm tra xem sản phẩm có bị ẩn không
        if (product.hidden || product.so_luong === 0) {
            console.warn("Sản phẩm bị ẩn:", product);
            return; // Bỏ qua sản phẩm này
        }

        // Tính giá sau giảm
        const giaGoc = product.gia;
        const giamGia = product.giam_gia || 0; // Nếu không có giảm giá thì mặc định là 0
        const giaSauGiam = giaGoc - (giaGoc * giamGia / 100);

        const productCard = document.createElement("div");
        productCard.classList.add("col-md-4");
        productCard.innerHTML = `
            <div class="card mb-3">
                <img src="${product.hinh_anh}" class="card-img-top" alt="${product.ten_san_pham}">
                <div class="card-body">
                    <h5 class="card-title">${product.ten_san_pham}</h5>
                    <!-- Hiển thị giá và giảm giá -->
                    ${giamGia > 0 
                        ? `<p class="text-danger"><del>${giaGoc.toLocaleString()} VND</del> <strong>${giaSauGiam.toLocaleString()} VND</strong></p>
                           <p class="badge bg-success">Giảm ${giamGia}%</p>` 
                        : `<p>${giaGoc.toLocaleString()} VND</p>`}
                        
                    <p class="text-muted">📦 Tồn kho: <strong>${product.so_luong}</strong></p>
                    
                    <a href="/products/${product.id}/" class="btn btn-detail">Chi Tiết</a>
                    <button class="btn btn-primary" onclick="addToCart(${product.id})">🛒 Thêm vào giỏ hàng</button>
                </div>
            </div>
        `;
        productList.appendChild(productCard);
    });
}

// 🌟 Thêm debounce để tránh spam API
function debounce(func, delay) {
    let timer;
    return function () {
        clearTimeout(timer);
        timer = setTimeout(() => func(), delay);
    };
}

const applyFilters = debounce(() => {
    let filteredProducts = [...allProducts]; // Clone danh sách sản phẩm

    const searchQuery = document.getElementById("search-input").value.toLowerCase();
    const category = document.getElementById("category-filter").value;
    const brand = document.getElementById("brand-filter").value;
    const minPrice = parseFloat(document.getElementById("min-price").value);
    const maxPrice = parseFloat(document.getElementById("max-price").value);
    const sortOption = document.getElementById("sort-filter").value;

    // 🔍 Lọc theo từ khóa
    if (searchQuery) {
        filteredProducts = filteredProducts.filter((p) =>
            p.ten_san_pham.toLowerCase().includes(searchQuery)
        );
    }

    // 📌 Lọc theo danh mục
    if (category) {
        filteredProducts = filteredProducts.filter(p => p.danh_muc === category);
    }

    // 🔥 Lọc theo thương hiệu
    if (brand) {
        filteredProducts = filteredProducts.filter(p => p.thuong_hieu === brand);
    }

    // 💰 Lọc theo khoảng giá
    if (!isNaN(minPrice)) {
        filteredProducts = filteredProducts.filter(p => p.gia >= minPrice);
    }
    if (!isNaN(maxPrice)) {
        filteredProducts = filteredProducts.filter(p => p.gia <= maxPrice);
    }

    // 🔄 Sắp xếp sản phẩm
    if (sortOption === "price-asc") {
        filteredProducts.sort((a, b) => a.gia - b.gia);
    } else if (sortOption === "price-desc") {
        filteredProducts.sort((a, b) => b.gia - a.gia);
    } else if (sortOption === "newest") {
        filteredProducts.sort((a, b) => new Date(b.ngay_tao) - new Date(a.ngay_tao));
    }

    renderProducts(filteredProducts);
}, 500);

// 🎯 Load danh mục & thương hiệu vào select box
function loadFilterOptions(products) {
    const categories = [...new Set(products.map(p => p.danh_muc))];
    const brands = [...new Set(products.map(p => p.thuong_hieu))];

    const categorySelect = document.getElementById("category-filter");
    const brandSelect = document.getElementById("brand-filter");

    categorySelect.innerHTML = `<option value="">Tất cả</option>`;
    brandSelect.innerHTML = `<option value="">Tất cả</option>`;

    categories.forEach(category => {
        categorySelect.innerHTML += `<option value="${category}">${category}</option>`;
    });

    brands.forEach(brand => {
        brandSelect.innerHTML += `<option value="${brand}">${brand}</option>`;
    });
}

// Sự kiện thay đổi bộ lọc
document.getElementById("search-input").addEventListener("input", applyFilters);
document.getElementById("category-filter").addEventListener("change", applyFilters);
document.getElementById("brand-filter").addEventListener("change", applyFilters);
document.getElementById("min-price").addEventListener("input", applyFilters);
document.getElementById("max-price").addEventListener("input", applyFilters);
document.getElementById("sort-filter").addEventListener("change", applyFilters);

document.addEventListener("DOMContentLoaded", fetchProducts);
