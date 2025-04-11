
# Create your models here.
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from django.db.models import Sum, F, ExpressionWrapper, DecimalField
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import uuid
from datetime import datetime

# người dùng
class User(AbstractUser):
    so_dien_thoai = models.CharField(max_length=20, unique=True, null=True)
    dia_chi = models.TextField(null=True, blank=True)
    vai_tro = models.CharField(max_length=20, choices=[('admin', 'Admin'), ('khach_hang', 'Khách hàng')], default='khach_hang')

    # Sửa lỗi trùng lặp với auth.User
    groups = models.ManyToManyField(
        "auth.Group",
        related_name="+",  # Tránh lỗi trùng lặp
        blank=True
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="+",  # Tránh lỗi trùng lặp
        blank=True
    )

    def __str__(self):
        return self.username


# Danh mục sản phẩm
class Category(models.Model):
    ten_danh_muc = models.CharField(max_length=255, unique=True)
    mo_ta = models.TextField(null=True, blank=True)
    ngay_tao = models.DateTimeField(default=now)  

    def __str__(self):
        return self.ten_danh_muc

# Sản phẩm
class Product(models.Model):
    ten_san_pham = models.CharField(max_length=255)
    mo_ta = models.TextField()
    gia = models.DecimalField(max_digits=10, decimal_places=0)
    giam_gia = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Cho phép số lẻ
    so_luong = models.IntegerField(default=0)
    so_luong_ban = models.IntegerField(default=0) 
    danh_muc = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    thuong_hieu = models.CharField(max_length=50, null=True, blank=True)
    kich_co = models.CharField(max_length=10, choices=[(str(i), str(i)) for i in range(36, 46)])
    mau_sac = models.CharField(max_length=50)
    chat_lieu = models.CharField(max_length=100, null=True, blank=True)
    
    gioi_tinh = models.CharField(
        max_length=10,
        choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Unisex', 'Unisex')],
        default='Unisex'
    )

    hinh_anh = models.URLField(max_length=255, null=True, blank=True)  # ✅ Sử dụng URL hình ảnh

    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ten_san_pham
    


    def get_final_price(self):
        return self.gia * (Decimal(1) - self.giam_gia / Decimal(100))
    
    @property
    def ton_kho_thuc_te(self):
        """ Tính tồn kho thực tế dựa trên số lượng đang giữ trong giỏ hàng """
        reserved_quantity = self.cartitem_set.aggregate(Sum('so_luong'))['so_luong__sum'] or 0
        return max(0, self.so_luong - reserved_quantity)


# giỏ hàng
User = get_user_model()  # Lấy model người dùng hiện tại
class Cart(models.Model):
    nguoi_dung = models.ForeignKey(User, on_delete=models.CASCADE)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Giỏ hàng của {self.nguoi_dung.username}"

# chi tiết giỏ hàng
class CartItem(models.Model):
    gio_hang = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="cart_items")
    san_pham = models.ForeignKey(Product, on_delete=models.CASCADE)
    so_luong = models.IntegerField(default=1)
    gia_sau_giam = models.DecimalField(max_digits=10, decimal_places=0, default=0)  # ✅ Thêm trường này

    def __str__(self):
        return f"{self.san_pham.ten_san_pham} - {self.so_luong}"

class Order(models.Model):
    PHUONG_THUC_THANH_TOAN = [
        ("cod", "Thanh toán khi nhận hàng"),
        ("online", "Thanh toán Online"),
    ]

    PHUONG_THUC_ONLINE = [
        ("momo", "MoMo"),
        ("zalopay", "ZaloPay"),
        ("vnpay", "VNPay"),
    ]

    TRANG_THAI_DON_HANG = [
        ("dang_xu_ly", "Đang xử lý"),
        ("da_xu_ly", "Đã xử lý"),
        ("cho_giao_hang", "Chờ giao hàng"),
        ("dang_giao_hang", "Đang giao hàng"),
        ("da_giao_hang", "Đã giao hàng"),
        ("da_huy", "Đã hủy"),
    ]
    created_at = models.DateTimeField(auto_now_add=True)  
    nguoi_dung = models.ForeignKey(User, on_delete=models.CASCADE)
    tong_tien = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    phuong_thuc_tt = models.CharField(max_length=10, choices=PHUONG_THUC_THANH_TOAN, default="cod")
    phuong_thuc_online = models.CharField(
        max_length=10, choices=PHUONG_THUC_ONLINE, null=True, blank=True
    )
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    trang_thai = models.CharField(
        max_length=20, choices=TRANG_THAI_DON_HANG, default="dang_xu_ly"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_total(self):
        total = sum(item.gia * item.so_luong for item in self.order_items.all())
        self.tong_tien = total
        self.save()

    def __str__(self):
        return f"Order {self.id} - {self.nguoi_dung.username} - {self.tong_tien}₫ - {self.get_trang_thai_display()}"


class OrderItem(models.Model):
    don_hang = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items")
    san_pham = models.ForeignKey("Product", on_delete=models.CASCADE)
    so_luong = models.PositiveIntegerField()
    gia = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        # Kiểm tra nếu số lượng đặt hàng vượt quá số lượng tồn kho
        if self.so_luong > self.san_pham.so_luong:
            raise ValidationError(_("Số lượng sản phẩm không đủ!"))

        super().save(*args, **kwargs)  # Lưu trước khi cập nhật số lượng tồn kho

        # Cập nhật số lượng tồn kho và số lượng bán
        self.san_pham.__class__.objects.filter(id=self.san_pham.id).update(
            so_luong=F("so_luong") - self.so_luong,
            so_luong_ban=F("so_luong_ban") + self.so_luong
        )

        # Tính lại tổng tiền cho đơn hàng sau khi thêm item mới
        self.don_hang.calculate_total()

    def __str__(self):
        return f"{self.san_pham.ten_san_pham} - {self.so_luong}x"



class Payment(models.Model):
    class PaymentMethod(models.TextChoices):
        VNPAY = 'VNPay', 'VNPay'
        MOMO = 'MoMo', 'MoMo'
        COD = 'COD', 'Thanh toán khi nhận hàng'

    class PaymentStatus(models.TextChoices):
        PENDING = 'Cho_xac_nhan', 'Chờ xác nhận'
        SUCCESS = 'Thanh_cong', 'Thành công'
        FAILED = 'That_bai', 'Thất bại'

    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name="payment")
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['transaction_id']),
        ]

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = self.generate_unique_transaction_id()
        super().save(*args, **kwargs)

    def generate_unique_transaction_id(self):
        """Tạo transaction_id duy nhất bằng cách kết hợp UUID và timestamp"""
        while True:
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            transaction_id = f'PAY_{timestamp}_{uuid.uuid4().hex.upper()}'
            if not Payment.objects.filter(transaction_id=transaction_id).exists():
                return transaction_id

    def __str__(self):
        return f"Thanh toán đơn {self.order.id} - {self.get_status_display()}"
    
# banner
class Banner(models.Model):
    tieu_de = models.CharField(max_length=255)
    hinh_anh = models.URLField()
    lien_ket = models.URLField(null=True, blank=True)
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tieu_de

# Đánh giá sản phẩm
class Review(models.Model):
    nguoi_dung = models.ForeignKey(User, on_delete=models.CASCADE)
    san_pham = models.ForeignKey(Product, on_delete=models.CASCADE)
    danh_gia = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])  # 1 - 5 sao
    binh_luan = models.TextField()
    ngay_tao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nguoi_dung.username} - {self.san_pham.ten_san_pham} ({self.danh_gia} sao)"