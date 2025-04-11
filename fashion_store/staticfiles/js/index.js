let displayedProducts = 6; // Số sản phẩm hiển thị ban đầu
let allProducts = []; // Lưu toàn bộ sản phẩm
async function fetchProducts() {
  try {
      const response = await fetch("/api/products/");
      const products = await response.json();

      console.log("📦 Dữ liệu sản phẩm:", products);

      if (!products || products.length === 0) {
          console.warn("⚠ Không có sản phẩm nào.");
          return;
      }

      products.sort((a, b) => b.id - a.id); // Sắp xếp ID giảm dần
      const visibleProducts = products.slice(0, 6); // Giới hạn số sản phẩm hiển thị

      const carouselList = document.getElementById("Carousel_list");
      const carouselIndicators = document.querySelector(".carousel-indicators");

      if (!carouselList || !carouselIndicators) {
          console.error("❌ Không tìm thấy phần tử Carousel_list hoặc carousel-indicators.");
          return;
      }

      carouselList.innerHTML = "";
      carouselIndicators.innerHTML = "";

      visibleProducts.forEach((product, index) => {
          console.log(`🔄 Đang thêm sản phẩm ${index + 1}: ${product.ten_san_pham}`);

          const productCard = document.createElement("div");
          productCard.classList.add("carousel-item");
          if (index === 0) productCard.classList.add("active");

          productCard.innerHTML = `
              <div class="row">
                  <div class="col-sm-5">
                      <div class="banner_taital">
                          <h1 class="banner_text" style="font-weight: bolder;">${product.ten_san_pham}</h1>
                          <h1 class="mens_text"><strong>Thương hiệu: ${product.thuong_hieu || "Thương hiệu"}</strong></h1>
                          <p class="lorem_text" style="font-size: 20px;">${product.mo_ta || "Mô tả sản phẩm."}</p>
                          <button class="buy_bt">Mua ngay</button>
                          <button class="more_bt"> <a href="${productAllUrl}" >Xem thêm</a></button>
                         
                      </div>
                  </div>
                  <div class="col-sm-5">
                      <div class="shoes_img">
                          <img src="${product.hinh_anh || "images/default.png"}" alt="${product.ten_san_pham}" style="height: 600px;">
                      </div>
                  </div>
              </div>
          `;


          carouselList.appendChild(productCard);

          // Tạo indicator
          const indicator = document.createElement("li");
          indicator.setAttribute("data-bs-target", "#myCarousel");
          indicator.setAttribute("data-bs-slide-to", index.toString());
          if (index === 0) indicator.classList.add("active");
          carouselIndicators.appendChild(indicator);
      });

        // chọn 2 sản phấm mới nhấtnhất
        const productList = document.getElementById("productList");
        productList.innerHTML = ""; // Xóa nội dung cũ

        products.slice(0, 2).forEach(product => { // Lấy 2 sản phẩm tiếp theo (trừ sản phẩm mới nhất)
            const productHTML = `
                <div class="col-md-6">
                    <div class="about-img" >
                        <button class="new_bt">New</button>
                        <div class="shoes-img">
                            <img src="${product.hinh_anh || "images/default.png"}" style="width: 80%; height: 350px;">
                        </div>
                        <p class="sport_text">${product.ten_san_pham}</p>
                        <div class="dolar_text">
                            <strong style="color:rgb(92, 92, 92); text-decoration: line-through;">${product.gia || "0"}.đ</strong>
                            <strong style="color:red;">-${product.giam_gia || "0"}%</strong>
                            <br>=><strong style="color: #f12a47; font-size: 30px;">${product.gia_sau_giam || "0"}.đ</strong>
                        </div>
                    </div>
                    <button class="seemore_bt">See More</button>
                </div>
            `;
            productList.innerHTML += productHTML;
        });

        // chọn sản phẩm có giảm giá cao nhất
        let bestDiscountProduct = products.reduce((max, product) => 
            (product.giam_gia > max.giam_gia ? product : max), products[0]);

        // Cập nhật giao diện
        const productone = document.getElementById("productone");
        productone.innerHTML = `
            <div class="col-md-8">
                <div class="shoes-img3">
                    <img src="${bestDiscountProduct.hinh_anh || 'images/default.png'}">
                </div>
            </div>
            <div class="col-md-4">
                <div class="sale_text">
                    <strong>Sale <br><span style="color: #0a0506;">${bestDiscountProduct.ten_san_pham}</span> <br>SHOES</strong>
                </div>
                <div class="number_text">
                    <strong><span style="color: #0a0506">${bestDiscountProduct.gia_sau_giam || "0"}.đ</span></strong>
                </div>
                <button class="seemore">See More</button>
            </div>
        `;


    // Sắp xếp sản phẩm theo số lượng tồn kho giảm dần và lấy 6 sản phẩm đầu tiên
    const topProducts = products.sort((a, b) => b.so_luong_ton - a.so_luong_ton).slice(0, 6);

    const productContainer = document.getElementById("productall");
    productContainer.innerHTML = ""; // Xóa nội dung cũ

    topProducts.forEach(product => {
        const productHTML = `
            <div class="col-sm-4">
                <div class="best_shoes">
                    <p class="best_text">${product.ten_san_pham}</p>
                    <div class="shoes_icon">
                        <img src="${product.hinh_anh || 'images/default.png'}" alt="${product.ten_san_pham}" style="height: 280px; !important;>
                    </div>
                        <div style="font-size: 20px;">Giá gốc: <strong style="color:rgb(92, 92, 92); text-decoration: line-through; ">${product.gia || "0"}.đ</strong></div>
                        <div class="shoes_price">Giá còn : <span style="color: #ff4e5b; font-weight: bolder;">${product.gia_sau_giam || product.gia}.đ</span></div>
                    </div>
                </div>
            </div>  
        `;
        productContainer.innerHTML += productHTML;
    });

    } catch (error) {
        console.error("❌ Lỗi khi tải sản phẩm:", error);
    }
}

// ✅ Gọi hàm khi trang tải
document.addEventListener("DOMContentLoaded", () => {
    fetchProducts();
    fetchLatestProduct();
});

    
  // Hiển thị thông báo
  function displayNotification(message, type = "success") {
    const container = document.getElementById("notification-container");
    if (!container) return;

    const notification = document.createElement("div");
    notification.className = `notification ${type}`;
    notification.style.padding = "10px 20px";
    notification.style.marginBottom = "10px";
    notification.style.borderRadius = "4px";
    notification.style.color = "#fff";
    notification.style.boxShadow = "0 0 10px rgba(0,0,0,0.1)";
    notification.style.opacity = "0";
    notification.style.transition = "opacity 0.5s ease";

    // Đặt màu nền theo loại thông báo
    if (type === "success") {
      notification.style.backgroundColor = "#28a745";
    } else if (type === "error") {
      notification.style.backgroundColor = "#dc3545";
    } else {
      notification.style.backgroundColor = "#007bff";
    }

    notification.innerText = message;
    container.appendChild(notification);

    // Hiển thị thông báo (fade in)
    setTimeout(() => {
      notification.style.opacity = "1";
    }, 100);

    // Ẩn và xóa thông báo sau 3 giây
    setTimeout(() => {
      notification.style.opacity = "0";
      setTimeout(() => {
        container.removeChild(notification);
      }, 500);
    }, 3000);
  }

  // Thêm sản phẩm vào giỏ hàng
  async function addToCart(productId) {
    console.log("Adding product ID:", productId);
    const accessToken = localStorage.getItem("access_token");
    if (!accessToken) {
      displayNotification(
        "Bạn cần đăng nhập để thêm sản phẩm vào giỏ hàng.",
        "error"
      );
      window.location.href = "{% url 'login' %}";
      return;
    }

    try {
      const response = await fetch("/api/cart/add/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ san_pham_id: productId, so_luong: 1 }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.message || "Lỗi không xác định khi thêm sản phẩm."
        );
      }

      displayNotification("Sản phẩm đã thêm vào giỏ hàng!", "success");

      // ✅ Tự động cập nhật giao diện giỏ hàng mà không load lại trang
      updateCartUI(data.cart);
    } catch (error) {
      console.error("Lỗi khi thêm sản phẩm:", error);
      displayNotification(
        "Có lỗi xảy ra khi thêm sản phẩm vào giỏ hàng.",
        "error"
      );
    }
  }

  // 🔄 Hàm cập nhật UI giỏ hàng mà không cần load lại trang
  function updateCartUI(cart) {
    const cartCounter = document.getElementById("cart-count");
    if (cartCounter) {
      cartCounter.textContent = cart.tong_san_pham || 0;
    }
  }
