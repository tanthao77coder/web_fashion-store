import os
import django
from decimal import Decimal
from collections import defaultdict

# Thiết lập môi trường Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fashion_store.settings")
django.setup()

from store.models import Product, Category

# Tạo danh mục nếu chưa có
danh_muc_the_thao, _ = Category.objects.get_or_create(ten_danh_muc="Giày thể thao")
danh_muc_binh_thuong, _ = Category.objects.get_or_create(ten_danh_muc="Giày bình thường")

# Danh sách sản phẩm mẫu
products = [
    {"ten": "Nike Air Force 1", "gia": "2500000", "giam_gia": "10.00", "kich_co": "42", "mau_sac": "Trắng", "thuong_hieu": "Nike"},
    {"ten": "Nike ZoomX", "gia": "3200000", "giam_gia": "15.00", "kich_co": "41", "mau_sac": "Đen", "thuong_hieu": "Nike"},
    {"ten": "Adidas Ultraboost", "gia": "2800000", "giam_gia": "5.00", "kich_co": "40", "mau_sac": "Xanh", "thuong_hieu": "Adidas"},
    {"ten": "Adidas Superstar", "gia": "1500000", "giam_gia": "8.00", "kich_co": "43", "mau_sac": "Đỏ", "thuong_hieu": "Adidas"},
    {"ten": "Puma RS-X", "gia": "1900000", "giam_gia": "12.00", "kich_co": "39", "mau_sac": "Đen trắng", "thuong_hieu": "Puma"},
    {"ten": "Converse Chuck Taylor", "gia": "2700000", "giam_gia": "7.00", "kich_co": "42", "mau_sac": "Xám", "thuong_hieu": "Converse"},
    {"ten": "Vans Old Skool", "gia": "2200000", "giam_gia": "9.00", "kich_co": "41", "mau_sac": "Trắng", "thuong_hieu": "Vans"},
    {"ten": "Reebok Classic", "gia": "2100000", "giam_gia": "11.00", "kich_co": "40", "mau_sac": "Hồng", "thuong_hieu": "Reebok"},
    {"ten": "Fila Disruptor", "gia": "2900000", "giam_gia": "6.00", "kich_co": "44", "mau_sac": "Xanh navy", "thuong_hieu": "Fila"},
    {"ten": "Jordan 1 Retro", "gia": "4500000", "giam_gia": "20.00", "kich_co": "42", "mau_sac": "Trắng đỏ", "thuong_hieu": "Jordan"},
]

# Đếm số lượng sản phẩm theo thương hiệu và danh mục
brand_count = defaultdict(int)
category_count = defaultdict(int)

# Danh mục xen kẽ để tránh quá 3 sản phẩm cùng danh mục
categories = [danh_muc_the_thao, danh_muc_binh_thuong]
category_index = 0

# Thêm sản phẩm vào database
for p in products:
    # Kiểm tra số lượng sản phẩm theo thương hiệu
    if brand_count[p["thuong_hieu"]] >= 2:
        print(f"❌ Bỏ qua {p['ten']}: Đã có 2 sản phẩm của thương hiệu {p['thuong_hieu']}")
        continue

    # Chọn danh mục xen kẽ để không vượt quá 3 sản phẩm mỗi danh mục
    selected_category = categories[category_index]
    if category_count[selected_category.ten_danh_muc] >= 3:
        category_index = (category_index + 1) % len(categories)
        selected_category = categories[category_index]

    # Tạo sản phẩm
    product = Product.objects.create(
        ten_san_pham=p["ten"],
        mo_ta=f"Mẫu giày thể thao {p['thuong_hieu']} phong cách, phù hợp nhiều hoàn cảnh.",
        gia=Decimal(p["gia"]),
        giam_gia=Decimal(p["giam_gia"]),
        so_luong=50,
        danh_muc=selected_category,
        thuong_hieu=p["thuong_hieu"],
        kich_co=p["kich_co"],
        mau_sac=p["mau_sac"],
        chat_lieu="Da tổng hợp",
        gioi_tinh="Unisex",
        hinh_anh=f"https://example.com/{p['ten'].lower().replace(' ', '-')}.jpg",
    )

    # Cập nhật bộ đếm
    brand_count[p["thuong_hieu"]] += 1
    category_count[selected_category.ten_danh_muc] += 1

    print(f"✅ Đã thêm sản phẩm: {product.ten_san_pham} vào danh mục {selected_category.ten_danh_muc}")

print("🎉 Hoàn thành thêm sản phẩm vào database!")
