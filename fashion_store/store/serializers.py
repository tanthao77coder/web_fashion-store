from django.contrib.auth import get_user_model
from rest_framework import serializers , viewsets
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Payment
from django.contrib.auth.password_validation import validate_password
from django.db.models import Sum


User = get_user_model()  # Lấy model User đúng

# ✅ API của người dùngUser = get_user_model()  # Lấy model User mở rộng của bạn
class UserSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)  # Xác nhận mật khẩu

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'so_dien_thoai', 'dia_chi', 'vai_tro']
        extra_kwargs = {
            'password': {'write_only': True},
            'username': {'required': True}
        }

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")
        password2 = attrs.get("password2")

        # Kiểm tra username đã tồn tại chưa
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError({"username": "Tên đăng nhập đã tồn tại!"})

        # Kiểm tra email đã tồn tại chưa (nếu muốn email là duy nhất)
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({"email": "Email đã được sử dụng!"})

        # Kiểm tra mật khẩu có khớp không
        if password != password2:
            raise serializers.ValidationError({"password": "Mật khẩu không khớp!"})

        try:
            validate_password(password)
        except serializers.ValidationError as e:
            raise serializers.ValidationError({"password": e.messages})

        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')  # Xóa password2 trước khi lưu

        if not validated_data.get("username"):
            validated_data["username"] = validated_data["email"].split("@")[0]  # Lấy phần trước @ của email làm username
        
        user = User.objects.create_user(**validated_data)  # Tạo user
        return user


# Serializer dùng để lấy và cập nhật thông tin người dùng (không cập nhật mật khẩu)
class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # Bao gồm các trường bạn muốn cho phép cập nhật (có thể thêm phone, address nếu model có)
        fields = ['id', 'username', 'email', 'so_dien_thoai', 'dia_chi', 'vai_tro']  # Các trường cần cập nhật
        extra_kwargs = {
            'username': {'required': False},  # Không bắt buộc khi cập nhật
            'email': {'required': False},     # Không bắt buộc khi cập nhật
            'so_dien_thoai': {'required': False},  # Số điện thoại không bắt buộc khi cập nhật
            'dia_chi': {'required': False},       # Địa chỉ không bắt buộc khi cập nhật
            'vai_tro': {'required': False},       # Vai trò không bắt buộc khi cập nhật
        }

# Serializer dùng cho đổi mật khẩu
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)

    def validate(self, data):
        if data['new_password'] != data['new_password2']:
            raise serializers.ValidationError("Mật khẩu mới không khớp!")
        return data

# ✅ API của sản phẩm
class CategorySerializer(serializers.ModelSerializer):
    """✅ Serializer để quản lý danh mục sản phẩm"""
    
    class Meta:
        model = Category
        fields = ['id', 'ten_danh_muc', 'mo_ta', 'ngay_tao']
        extra_kwargs = {
            'ten_danh_muc': {'required': True},  # Bắt buộc nhập tên danh mục
            'mo_ta': {'required': False}  # Mô tả không bắt buộc
        }

    def validate_ten_danh_muc(self, value):
        """🔴 Không cho phép tên danh mục trùng lặp"""
        if Category.objects.filter(ten_danh_muc=value).exists():
            raise serializers.ValidationError("Danh mục này đã tồn tại!")
        return value
    
# ------------------------------------------------------

# ✅ Serializer cho sản phẩm (Product)
class ProductSerializer(serializers.ModelSerializer):
    danh_muc = serializers.StringRelatedField(read_only=True)  
    danh_muc_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    ton_kho_thuc_te = serializers.SerializerMethodField()
    gia = serializers.IntegerField(required=True)
    so_luong = serializers.IntegerField(required=True)
    gia_sau_giam = serializers.SerializerMethodField()
    is_out_of_stock = serializers.SerializerMethodField()  # ✅ Thêm trường kiểm tra hết hàng

    class Meta:
        model = Product
        fields = [
            'id', 'ten_san_pham', 'mo_ta', 'gia', 'giam_gia', 'gia_sau_giam',
            'so_luong', 'kich_co', 'mau_sac', 'thuong_hieu', 'chat_lieu', 
            'gioi_tinh', 'hinh_anh', 'danh_muc', 'danh_muc_id', 'ton_kho_thuc_te',
            'is_out_of_stock'  # ✅ Thêm vào danh sách fields
        ]

    def get_ton_kho_thuc_te(self, obj):
        """ Tính tồn kho thực tế (trừ số lượng đã đặt hàng) """
        reserved_quantity = CartItem.objects.filter(san_pham=obj).aggregate(Sum('so_luong'))['so_luong__sum'] or 0
        return obj.so_luong - reserved_quantity

    def get_is_out_of_stock(self, obj):
        """ Kiểm tra sản phẩm có hết hàng không """
        return self.get_ton_kho_thuc_te(obj) <= 0  # ✅ Hết hàng khi số lượng <= 0

    def get_gia_sau_giam(self, obj):
        """Tính giá sau giảm."""
        return obj.gia - (obj.gia * obj.giam_gia / 100) if obj.giam_gia else obj.gia

    def validate_gia(self, value):
        if value <= 0:
            raise serializers.ValidationError("Giá sản phẩm phải lớn hơn 0.")
        return value

    def validate_so_luong(self, value):
        if value < 0:
            raise serializers.ValidationError("Số lượng sản phẩm không thể âm.")
        return value

    def create(self, validated_data):
        danh_muc = validated_data.pop('danh_muc_id')
        if not danh_muc:
            raise serializers.ValidationError({"danh_muc_id": "Danh mục sản phẩm là bắt buộc."})
        
        return Product.objects.create(danh_muc=danh_muc, **validated_data)

    def update(self, instance, validated_data):
        instance.ten_san_pham = validated_data.get('ten_san_pham', instance.ten_san_pham)
        instance.mo_ta = validated_data.get('mo_ta', instance.mo_ta)
        instance.gia = validated_data.get('gia', instance.gia)
        instance.giam_gia = validated_data.get('giam_gia', instance.giam_gia)
        instance.so_luong = validated_data.get('so_luong', instance.so_luong)

        danh_muc = validated_data.get('danh_muc_id', None)
        if danh_muc:
            instance.danh_muc = danh_muc

        instance.save()
        return instance

#-----------------------------------------------------------

class CartItemSerializer(serializers.ModelSerializer):
    san_pham = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'gio_hang', 'san_pham', 'so_luong']
        extra_kwargs = {
            'gio_hang': {'read_only': True},
        }

class CartSerializer(serializers.ModelSerializer):
    san_pham_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(), write_only=True
    )
    so_luong = serializers.IntegerField(write_only=True, default=1)
    items = CartItemSerializer(many=True, read_only=True, source='cart_items')
    total_quantity = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'nguoi_dung', 'san_pham_id', 'so_luong', 'items', 'total_quantity']
        extra_kwargs = {
            'nguoi_dung': {'read_only': True}
        }

    def get_total_quantity(self, obj):
        return sum(item.so_luong for item in obj.cart_items.all())

    def create(self, validated_data):
        user = self.context['request'].user
        san_pham = validated_data.pop('san_pham_id')
        so_luong = validated_data.pop('so_luong', 1)

        # Lấy hoặc tạo giỏ hàng
        gio_hang, _ = Cart.objects.get_or_create(nguoi_dung=user)
        cart_item, created = CartItem.objects.get_or_create(
            gio_hang=gio_hang, san_pham=san_pham,
            defaults={'so_luong': so_luong}
        )

        if not created:
            cart_item.so_luong += so_luong
            cart_item.save()

        return gio_hang

    def update(self, instance, validated_data):
        user = self.context['request'].user
        san_pham = validated_data.get('san_pham_id')
        so_luong = validated_data.get('so_luong', 1)

        # Kiểm tra giỏ hàng của user
        gio_hang = Cart.objects.filter(nguoi_dung=user).first()
        if not gio_hang:
            raise serializers.ValidationError({"detail": "Giỏ hàng không tồn tại."})

        # Kiểm tra sản phẩm trong giỏ hàng
        try:
            cart_item = CartItem.objects.get(gio_hang=gio_hang, san_pham=san_pham)
        except CartItem.DoesNotExist:
            raise serializers.ValidationError({"san_pham_id": "Sản phẩm không có trong giỏ hàng."})

        # Xóa nếu số lượng <= 0
        if so_luong <= 0:
            cart_item.delete()
            return gio_hang  

        # Cập nhật số lượng sản phẩm trong giỏ hàng
        cart_item.so_luong = so_luong
        cart_item.save()
        
        return gio_hang


# đơn hàng
# ✅ Serializer Chi tiết sản phẩm trong đơn hàng
class OrderItemSerializer(serializers.ModelSerializer):
    san_pham = serializers.StringRelatedField()  # 👈 Hiển thị tên sản phẩm thay vì ID

    class Meta:
        model = OrderItem
        fields = ['id', 'san_pham', 'so_luong', 'gia']
        read_only_fields = ['id']

class OrderSerializer(serializers.ModelSerializer):
    total_amount = serializers.DecimalField(source="tong_tien", max_digits=10, decimal_places=2, read_only=True)
    status = serializers.CharField(source="trang_thai", read_only=True)
    status_display = serializers.CharField(source="get_trang_thai_display", read_only=True)  # ✅ Hiển thị trạng thái thân thiện
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'total_amount',
            'status',
            'status_display',  # ✅ Thêm trường này để hiển thị dạng text
            'phuong_thuc_tt',
            'phuong_thuc_online',
            'transaction_id',
            'created_at',
            'order_items'
        ]


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'nguoi_dung', 'tong_gia', 'phuong_thuc_tt', 'trang_thai', 'ngay_tao']
        read_only_fields = ['id', 'nguoi_dung', 'tong_gia', 'trang_thai', 'ngay_tao']

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = CartItem.objects.filter(nguoi_dung=user)
        
        if not cart_items.exists():
            raise serializers.ValidationError("Giỏ hàng của bạn đang trống.")
        
        # Tính tổng giá trị đơn hàng
        tong_gia = sum(item.san_pham.get_final_price() * item.so_luong for item in cart_items)
        
        # Tạo đơn hàng
        order = Order.objects.create(nguoi_dung=user, tong_gia=tong_gia, **validated_data)
        
        # Tạo OrderItem và cập nhật tồn kho
        for item in cart_items:
            OrderItem.objects.create(
                don_hang=order,
                san_pham=item.san_pham,
                so_luong=item.so_luong,
                gia=item.san_pham.get_final_price()
            )
            
            # Cập nhật số lượng tồn kho
            item.san_pham.so_luong -= item.so_luong
            item.san_pham.save()
        
        # Xóa giỏ hàng sau khi đặt hàng thành công
        cart_items.delete()
        
        return order



#-----------------------------------
class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(source='order.id')  # Trả về ID của đơn hàng liên quan
    payment_method_display = serializers.CharField(source='get_payment_method_display')  # Hiển thị tên phương thức thanh toán
    status_display = serializers.CharField(source='get_status_display')  # Hiển thị tên trạng thái thanh toán

    class Meta:
        model = Payment
        fields = ['id', 'order_id', 'payment_method', 'payment_method_display', 'status', 'status_display', 'transaction_id', 'created_at']

