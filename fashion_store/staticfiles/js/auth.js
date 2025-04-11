document.addEventListener("DOMContentLoaded", function () {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");

    // 🟢 Xử lý đăng nhập
    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            let username = document.getElementById("username").value;
            let password = document.getElementById("password").value;

            let response = await fetch("/api/auth/login/", { 
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username, password })
            });

            let result = await response.json();
            if (response.ok) {
                localStorage.setItem("access_token", result.access);
                alert("Đăng nhập thành công!");

                // 🔥 Kiểm tra trang trước và redirect hợp lý
                if (document.referrer && !document.referrer.includes("/login")) {
                    window.location.href = document.referrer;
                } else {
                    window.location.href = "/";
                }
            } else {
                alert("Lỗi: " + (result.detail || JSON.stringify(result)));
            }
        });
    }

    // 🟢 Xử lý đăng ký
    if (registerForm) {
        registerForm.addEventListener("submit", async function (event) {
            event.preventDefault();
    
            let userData = {
                username: document.getElementById("username").value,
                email: document.getElementById("email").value,
                password: document.getElementById("password").value,
                password2: document.getElementById("password2").value, // Thêm password2
            };
    
            let response = await fetch("/api/auth/register/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(userData)
            });
    
            let result = await response.json();
            if (response.ok) {
                alert("Đăng ký thành công! Hãy đăng nhập.");
                window.location.href = "/login/";
            } else {
                alert("Lỗi: " + JSON.stringify(result));
            }
        });
    }    
});

// 🟢 Lấy thông tin người dùng
async function fetchUserInfo() {
    const accessToken = localStorage.getItem("access_token");

    if (!accessToken) return;

    try {
        let response = await fetch("/api/auth/user/", {
            method: "GET",
            headers: { "Authorization": `Bearer ${accessToken}` }
        });

        if (response.ok) {
            let user = await response.json();
            localStorage.setItem("user_info", JSON.stringify(user)); // Lưu thông tin vào localStorage
            console.log("Token lưu vào localStorage:", localStorage.getItem("access_token"));

        } else if (response.status === 401) {
            localStorage.removeItem("access_token");
            window.location.href = "/login/";
        }
    } catch (error) {
        console.error("Lỗi khi tải thông tin người dùng:", error);
    }
}
 
// Gọi hàm khi trang tải
document.addEventListener("DOMContentLoaded", fetchUserInfo);

document.addEventListener('DOMContentLoaded', async function () {
    const accessToken = localStorage.getItem('access_token');
    const authLinks = document.getElementById("auth-links");

    if (!authLinks) return;

    if (!accessToken) {
        authLinks.innerHTML = `<li class="nav-item"><a class="nav-link" href="${loginUrl}">Đăng nhập</a></li>`;
        return;
    }

    try {
        let response = await fetch("/api/auth/user/", {
            method: "GET",
            headers: { "Authorization": `Bearer ${accessToken}` }
        });

        if (response.ok) {
            let user = await response.json();
            authLinks.innerHTML = `
                <li class="nav-item dropdown">
                    <a class="nav-link dropdown-toggle" href="#" id="userDropdown" role="button" data-bs-toggle="dropdown">
                        <span>${user.username}</span>
                    </a>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="${profileUrl}">Thông tin cá nhân</a></li>
                        <li><hr class="dropdown-divider"></li>
                        <li><a class="dropdown-item text-danger" href="#" onclick="logout()">Đăng xuất</a></li>
                    </ul>
                </li>
            `;
        } else {
            authLinks.innerHTML = `<li class="nav-item"><a class="nav-link" href="${loginUrl}">Đăng nhập</a></li>`;
        }
    } catch (error) {
        console.error("Lỗi kết nối API.");
        authLinks.innerHTML = `<li class="nav-item"><a class="nav-link" href="${loginUrl}">Đăng nhập</a></li>`;
    }
});

function logout() {
    $('#logoutModal').modal('show');
}

function confirmLogout() {
    // Xóa token đăng nhập
    localStorage.removeItem("access_token");
    localStorage.removeItem("user_info");

    // Đóng modal ngay lập tức
    var logoutModal = document.getElementById('logoutModal');
    var modalInstance = bootstrap.Modal.getInstance(logoutModal);
    if (modalInstance) {
        modalInstance.hide();
    }

    // Đợi modal ẩn hoàn toàn, sau đó chuyển hướng
    logoutModal.addEventListener('hidden.bs.modal', function () {
        window.location.href = "/";
    }, { once: true }); // Sự kiện chỉ kích hoạt một lần
}







