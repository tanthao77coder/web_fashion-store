from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework import status
from .models import Payment
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import generics, serializers, permissions, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from .models import Cart, CartItem, Product, Category, Order, Payment, OrderItem
from .serializers import ProductSerializer, CartItemSerializer, UserSerializer, CategorySerializer,OrderSerializer, CreateOrderSerializer, PaymentSerializer
from django_filters.rest_framework import DjangoFilterBackend  # ✅ Bộ lọc theo trường
from rest_framework import filters  # ✅ Bộ lọc tìm kiếm, sắp xếp
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .serializers import CartSerializer, ChangePasswordSerializer
from django.db import transaction
import logging, requests
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from django.db.models import Sum , F
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import uuid
from .serializers import UserUpdateSerializer
from decimal import Decimal


User = get_user_model()  # Lấy model User đúng
# Khởi tạo logger
logger = logging.getLogger(__name__)

from django.shortcuts import render

def profile_view(request):
    return render(request, "profile.html", {"user": request.user})

def cart_view(request):
    return render(request, 'cart.html')


def productall_view(request):
    return render(request, 'product.html') 


def contact_view(request):
    return render(request, 'contact.html')


def sales_view(request):
    top_discount_products = Product.objects.order_by('-giam_gia')[:2]
    print("🔍 Dữ liệu sản phẩm:", top_discount_products) 
    return render(request, 'newsp.html', {'top_discount_products': top_discount_products})


@api_view(['GET'])
def get_order_history(request):
    # Lấy tất cả các đơn hàng của người dùng đang đăng nhập
    orders = Order.objects.filter(nguoi_dung=request.user)
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

# ✅ Trang chủ

def home_view(request):
    products = Product.objects.all()  # Lấy danh sách sản phẩm
    username = request.user.username if request.user.is_authenticated else None  # Lấy username nếu có

    return render(request, 'home.html', {'username': username, 'products': products})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            # Đăng nhập người dùng
            user = form.get_user()
            login(request, user)
            # Chuyển hướng người dùng đến trang chủ
            return redirect('home')  # Thay 'home' bằng tên URL trang chủ của bạn
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

# ✅ Trang đăng ký
def register_view(request):
    return render(request, 'register.html')

def product_detail(request, pk):
    # Lấy sản phẩm theo ID
    product = Product.objects.get(id=pk)
    return render(request, 'product_detail.html', {'product': product})

# ✅ API Đăng ký tài khoản
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

# ✅ API Đăng nhập lấy JWT Token

class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Đăng nhập người dùng và tạo JWT token
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                'access': access_token,
                'refresh': refresh_token,
                'username': user.username
            })

        return Response({"detail": "Invalid credentials"}, status=400)
    
# API lấy và cập nhật thông tin người dùng
class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    # Lấy thông tin người dùng
    def get(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user)  # Chuyển thông tin người dùng thành JSON
        return Response(serializer.data)  # Trả về thông tin người dùng

    # Cập nhật thông tin người dùng
    def put(self, request):
        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)  # Chỉ cập nhật những trường có trong request

        if serializer.is_valid():
            serializer.save()  # Lưu thông tin đã cập nhật
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# API đổi mật khẩu
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data.get("old_password")
            if not user.check_password(old_password):
                return Response({"old_password": ["Mật khẩu cũ không đúng."]}, status=status.HTTP_400_BAD_REQUEST)
            new_password = serializer.validated_data.get("new_password")
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Đổi mật khẩu thành công."})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# -------------------------------------------------------

class CategoryViewSet(viewsets.ModelViewSet):
    """✅ API CRUD cho Danh Mục Sản Phẩm"""
    
    queryset = Category.objects.all().order_by('-ngay_tao')
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]  # Ai cũng xem được, chỉ admin mới chỉnh sửa

    def perform_create(self, serializer):
        """✅ Chỉ admin mới được thêm danh mục"""
        if not self.request.user.is_staff:
            raise serializers.ValidationError({"error": "Bạn không có quyền thêm danh mục!"})
        serializer.save()

    def perform_update(self, serializer):
        """✅ Chỉ admin mới được cập nhật danh mục"""
        if not self.request.user.is_staff:
            raise serializers.ValidationError({"error": "Bạn không có quyền sửa danh mục!"})
        serializer.save()

    def perform_destroy(self, instance):
        """✅ Chỉ admin mới được xóa danh mục"""
        if not self.request.user.is_staff:
            raise serializers.ValidationError({"error": "Bạn không có quyền xóa danh mục!"})
        instance.delete()


# ✅ API products

# ✅ API Danh Sách & Thêm Sản Phẩm
class ProductListCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all().order_by('-ngay_tao')  # Sắp xếp sản phẩm mới nhất
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    # 🔎 Bộ lọc tìm kiếm
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    # Cập nhật filterset_fields để bao gồm 'thuong_hieu' và 'danh_muc'
    filterset_fields = ['danh_muc', 'gioi_tinh', 'kich_co', 'mau_sac', 'thuong_hieu']  # 'thuong_hieu' cho hãng và 'danh_muc' cho thể loại

    search_fields = ['ten_san_pham', 'mo_ta', 'thuong_hieu']  # Tìm kiếm theo tên sản phẩm, mô tả và hãng sản xuất
    ordering_fields = ['gia', 'ten_san_pham', 'ngay_tao']

    def create(self, request, *args, **kwargs):
        """ ✅ Chỉ admin mới có quyền thêm sản phẩm """
        if not request.user.is_staff:
            raise PermissionDenied("Bạn không có quyền thêm sản phẩm.")
        return super().create(request, *args, **kwargs)


# ✅ API Xem / Cập nhật / Xóa sản phẩm
# Cấu hình logging
logger = logging.getLogger(__name__)

class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        """ Lấy sản phẩm và tính toán tồn kho thực tế """
        product = super().get_object()

        # Lấy tổng số lượng sản phẩm đang trong giỏ hàng
        reserved_quantity = CartItem.objects.filter(san_pham=product).aggregate(Sum('so_luong'))['so_luong__sum'] or 0

        # Tồn kho thực tế
        product.ton_kho_thuc_te = max(0, product.so_luong - reserved_quantity)

        return product

    def update(self, request, *args, **kwargs):
        """ 
        ✅ Admin có thể chỉnh sửa tất cả
        ✅ Nhân viên chỉ có thể chỉnh sửa giá và mô tả
        ❌ Người dùng thường không có quyền chỉnh sửa
        """
        product = self.get_object()
        
        if request.user.is_superuser:
            logger.info(f"Admin {request.user.username} đã cập nhật sản phẩm: {product.ten_san_pham}")
            return super().update(request, *args, **kwargs)

        if request.user.is_staff:
            allowed_fields = ["gia", "mo_ta"]
            data = request.data.copy()

            for field in data.keys():
                if field not in allowed_fields:
                    raise PermissionDenied(f"Bạn không có quyền chỉnh sửa trường '{field}'.")

            logger.info(f"Nhân viên {request.user.username} đã cập nhật giá/mô tả sản phẩm: {product.ten_san_pham}")
            return super().update(request, *args, **kwargs)

        raise PermissionDenied("Bạn không có quyền chỉnh sửa sản phẩm này.")

    def destroy(self, request, *args, **kwargs):
        """ ✅ Chỉ admin mới có quyền xóa sản phẩm """
        product = self.get_object()

        if not request.user.is_superuser:
            raise PermissionDenied("Bạn không có quyền xóa sản phẩm.")

        logger.warning(f"Admin {request.user.username} đã xóa sản phẩm: {product.ten_san_pham}")
        return super().destroy(request, *args, **kwargs)
    
# Frontend chi tiết sản phẩm (sử dụng để render HTML)
def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk)

    # ✅ Tính tổng số lượng đang giữ trong giỏ hàng của tất cả user
    so_luong_giu_trong_gio = CartItem.objects.filter(san_pham=product).aggregate(total=Sum('so_luong'))['total'] or 0

    # ✅ Tồn kho thực tế
    ton_kho_thuc_te = product.so_luong - so_luong_giu_trong_gio

    return render(request, 'product_detail.html', {'product': product, 'ton_kho_thuc_te': ton_kho_thuc_te})
#---------------------------------------------------------

# ✅ API Xem giỏ hàng của người dùng
class CartDetailView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        print("Request user:", self.request.user)  # Debug
        cart, _ = Cart.objects.get_or_create(nguoi_dung=self.request.user)
        return cart

    
# API xem, tạo, cập nhật, xóa giỏ hàng
class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(nguoi_dung=self.request.user)
    
# API thêm sản phẩm vào giỏ hàng
class AddToCartView(generics.CreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(nguoi_dung=request.user)
        product_id = request.data.get('san_pham_id')
        so_luong = int(request.data.get('so_luong', 1))

        if so_luong <= 0:
            return Response({"error": "Số lượng phải lớn hơn 0!"}, status=status.HTTP_400_BAD_REQUEST)

        if not product_id:
            return Response({"error": "Thiếu product_id"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():  # 🔥 Đảm bảo dữ liệu đồng bộ
                product = Product.objects.select_for_update().get(id=product_id)

                # Kiểm tra tồn kho
                if product.so_luong < so_luong:
                    return Response({"error": "Số lượng sản phẩm không đủ trong kho!"}, status=status.HTTP_400_BAD_REQUEST)

                # Tính giá sau giảm
                gia_sau_giam = product.gia - (product.gia * product.giam_gia / 100)

                # Kiểm tra xem sản phẩm đã có trong giỏ hàng chưa
                cart_item, created = CartItem.objects.get_or_create(
                    gio_hang=cart, san_pham=product,
                    defaults={"so_luong": so_luong, "gia_sau_giam": gia_sau_giam}
                )

                if not created:
                    if cart_item.so_luong + so_luong > product.so_luong:
                        return Response({"error": "Số lượng sản phẩm trong kho không đủ!"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    cart_item.so_luong += so_luong
                    cart_item.save()

                # Cập nhật tồn kho
                product.so_luong -= so_luong
                product.save()

            return Response({
                "message": "Sản phẩm đã được thêm vào giỏ hàng.",
                "san_pham": product.ten_san_pham,
                "gia_sau_giam": gia_sau_giam,
                "so_luong_trong_gio": cart_item.so_luong,
                "ton_kho_con_lai": product.so_luong,
            }, status=status.HTTP_201_CREATED)

        except Product.DoesNotExist:
            return Response({"error": "Sản phẩm không tồn tại."}, status=status.HTTP_404_NOT_FOUND)

class CreateOrderView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        phuong_thuc_tt = request.data.get("phuong_thuc_tt", "cod")
        phuong_thuc_online = request.data.get("phuong_thuc_online", None)
        item_data = request.data.get("items")  # ✅ Lấy từ request body

        if not item_data:
            return Response({"error": "Không có sản phẩm nào được chọn!"}, status=400)

        item_ids = [int(item["san_pham_id"]) for item in item_data]  # ✅ Lấy danh sách ID từ request body
        cart_items = CartItem.objects.filter(
            gio_hang__nguoi_dung=user, san_pham__id__in=item_ids
        ).select_related("san_pham")

        if not cart_items.exists():
            return Response({"error": "Không tìm thấy sản phẩm trong giỏ hàng!"}, status=400)
                                                                                    

        # ✅ Kiểm tra tồn kho
        product_map = {item.san_pham.id: item.san_pham for item in cart_items}
        for item in cart_items:
            if item.so_luong > item.san_pham.so_luong:
                return Response({"error": f"Sản phẩm {item.san_pham.ten_san_pham} không đủ hàng!"}, status=400)

        with transaction.atomic():
            # ✅ Tạo đơn hàng
            transaction_id = f'PAY_{uuid.uuid4().hex.upper()}'
            order = Order.objects.create(
                nguoi_dung=user,
                tong_tien=0,  # Cập nhật sau
                phuong_thuc_tt=phuong_thuc_tt,
                phuong_thuc_online=phuong_thuc_online if phuong_thuc_tt == "online" else None,
                transaction_id=transaction_id,
            )

            # ✅ Tạo danh sách OrderItem
            order_items = []
            total_price = 0

            for item in cart_items:
                san_pham = product_map[item.san_pham.id]
                gia_san_pham = san_pham.get_final_price()
                so_luong = item.so_luong

                # ✅ Tạo OrderItem
                order_items.append(OrderItem(
                    don_hang_id=order.id,
                    san_pham=san_pham,
                    so_luong=so_luong,
                    gia=gia_san_pham,
                ))

                total_price += gia_san_pham * so_luong

                # ✅ Cập nhật số lượng tồn kho
                san_pham.so_luong -= so_luong
                san_pham.so_luong_ban += so_luong

            # ✅ Bulk insert OrderItem
            OrderItem.objects.bulk_create(order_items)

            # ✅ Cập nhật tổng tiền đơn hàng
            order.tong_tien = total_price
            order.save()

            # ✅ Cập nhật số lượng sản phẩm
            Product.objects.bulk_update(product_map.values(), ["so_luong", "so_luong_ban"])

            # ✅ Xóa sản phẩm được chọn khỏi giỏ hàng
            cart_items.delete()

            # ✅ Nếu giỏ hàng trống, xóa luôn giỏ hàng
            if not CartItem.objects.filter(gio_hang__nguoi_dung=user).exists():
                Cart.objects.filter(nguoi_dung=user).delete()

        return Response({
            "message": "Đặt hàng thành công!",
            "order_id": order.id,
            "transaction_id": order.transaction_id,
            "tong_tien": order.tong_tien,
        }, status=201)

# ✅ API Xem danh sách đơn hàng của người dùng
class UserOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(nguoi_dung=self.request.user).order_by('-created_at')


# ✅ API Xem chi tiết một đơn hàng
class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(nguoi_dung=self.request.user)

# ✅ API Hủy đơn hàng (Chỉ khi đơn hàng chưa giao)
class CancelOrderView(generics.UpdateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(nguoi_dung=self.request.user, trang_thai='Cho_xac_nhan')

    def update(self, request, *args, **kwargs):
        """ ✅ Hủy đơn hàng mà không cần gửi dữ liệu """
        instance = self.get_object()  # ✅ Lấy đơn hàng từ database
        instance.trang_thai = 'Da_huy'
        instance.save()
        return Response({"message": "Đơn hàng đã được hủy thành công."}, status=200)

# ✅ API Xóa Đơn Hàng (Chỉ khi đã hủy)
class DeleteOrderView(generics.DestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """ ✅ Lấy danh sách đơn hàng đã hủy của người dùng """
        return Order.objects.filter(nguoi_dung=self.request.user, trang_thai='Da_huy')

    def destroy(self, request, *args, **kwargs):
        """ ✅ Kiểm tra trạng thái trước khi xóa """
        instance = self.get_object()
        
        if instance.trang_thai != 'Da_huy':
            return Response({"error": "Chỉ có thể xóa đơn hàng đã hủy!"}, status=400)
        
        instance.delete()
        return Response({"message": "Đơn hàng đã được xóa thành công."}, status=200)

class UpdateCartItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):
        try:
            cart_item_id = kwargs.get("pk")  # Lấy ID sản phẩm từ URL
            cart_item = CartItem.objects.get(id=cart_item_id, gio_hang__nguoi_dung=request.user)
  # Chỉ cập nhật sản phẩm của chính user đó
            
            data = request.data  # Dữ liệu từ frontend
            serializer = CartItemSerializer(cart_item, data=data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({"message": "Cập nhật giỏ hàng thành công", "data": serializer.data}, status=200)
            
            return Response(serializer.errors, status=400)
        except CartItem.DoesNotExist:
            return Response({"error": "Không tìm thấy sản phẩm trong giỏ hàng!"}, status=404)

# API Xóa sản phẩm khỏi giỏ hàng
class RemoveFromCartView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(gio_hang__nguoi_dung=self.request.user)

    def perform_destroy(self, instance):
        # Hoàn lại số lượng sản phẩm vào kho
        instance.san_pham.so_luong += instance.so_luong
        instance.san_pham.save()
        instance.delete()

#-------------------------------------------

# ✅ API Thanh toán đơn hàng
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def process_payment(request):
    user = request.user
    print("User:", user)  # Kiểm tra user có được xác thực không
    return Response({"message": "Thanh toán thành công!"})

def pay_view(request):
    if request.method == "GET":
        selected_ids = request.GET.get("items", "").split(",")
        selected_items = CartItem.objects.filter(id__in=filter(str.isdigit, selected_ids))
        
        if not selected_items.exists():
            messages.error(request, "Không có sản phẩm hợp lệ trong giỏ hàng!")
            return render(request, "pay.html", {"selected_items": []})

        tong_gia = sum(item.san_pham.gia * (1 - (item.san_pham.giam_gia or 0) / 100) * item.so_luong for item in selected_items)

        return render(request, "pay.html", {"selected_items": selected_items, "tong_gia": tong_gia})

    elif request.method == "POST":
        if not request.user.is_authenticated:
            messages.error(request, "Bạn cần phải đăng nhập để thực hiện thanh toán.")
            return redirect('login')

        payment_method = request.POST.get("Payment.PaymentMethod")
        selected_items = CartItem.objects.filter(id__in=filter(str.isdigit, request.POST.getlist("selected_items")))

        if not selected_items.exists():
            messages.error(request, "Không có sản phẩm nào trong giỏ hàng!")
            return render(request, "pay.html", {"selected_items": []})

        with transaction.atomic():
            order = Order.objects.create(nguoi_dung=request.user, tong_tien=0, phuong_thuc_tt=payment_method)
            tong_gia = sum(
                (item.san_pham.gia * (1 - (item.san_pham.giam_gia or 0) / 100)) * item.so_luong
                for item in selected_items if item.san_pham.so_luong >= item.so_luong
            )

            if tong_gia == 0:
                messages.error(request, "Một hoặc nhiều sản phẩm không đủ số lượng!")
                return render(request, "pay.html", {"selected_items": selected_items})

            for item in selected_items:
                OrderItem.objects.create(san_pham=item.san_pham, so_luong=item.so_luong, gia=item.san_pham.gia, don_hang=order)

            order.tong_tien = tong_gia
            order.save()

            Payment.objects.create(order=order, payment_method=payment_method, status=Payment.PaymentStatus.SUCCESS, transaction_id=f"PAY_{order.id}_{payment_method.upper()}")
            order.trang_thai = "Da_thanh_toan"
            order.save()

        messages.success(request, "Thanh toán thành công!")
        return redirect('order-list')


class PaymentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        order_ids = request.data.get("don_hang_ids", [])
        payment_method = request.data.get("phuong_thuc_tt", "")

        if not order_ids or not isinstance(order_ids, list):
            return Response({"error": "Danh sách đơn hàng không hợp lệ!"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            orders = Order.objects.filter(id__in=order_ids, nguoi_dung=user)
            
            if orders.filter(payment__status="Thanh_cong").exists():
                return Response({"error": "Đơn hàng này đã được thanh toán!"}, status=status.HTTP_400_BAD_REQUEST)

            for order in orders:
                total_amount = round(Decimal(sum(item.gia * item.so_luong for item in order.order_items.all())), 2)
                order.tong_tien = total_amount
                order.save()
                
                # Nếu thanh toán COD thì trạng thái Payment là "cho_xac_nhan"
                payment_status = "cho_xac_nhan" if payment_method.lower() == "cod" else Payment.PaymentStatus.SUCCESS

                # Tạo bản ghi thanh toán
                Payment.objects.create(
                    order=order, 
                    payment_method=payment_method, 
                    status=payment_status,  # Cập nhật trạng thái Payment
                    transaction_id=f"PAY_{order.id}_{payment_method.upper()}"
                )
                
                # Cập nhật trạng thái đơn hàng
                order.trang_thai = "dang_xu_ly"
                order.save()

        return Response({"message": "Thanh toán thành công!"}, status=status.HTTP_201_CREATED)

class UserPaymentListView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__nguoi_dung=self.request.user)


# ✅ API Xem chi tiết thanh toán
class PaymentDetailView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Payment.objects.filter(order__nguoi_dung=self.request.user)  # Sử dụng 'order' thay vì 'don_hang'

class CancelPaymentView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return Payment.objects.all()

    def perform_update(self, serializer):
        instance = serializer.instance

        # Sử dụng Payment.PaymentStatus để so sánh trạng thái thanh toán
        if instance.status == Payment.PaymentStatus.FAILED:
            return Response({"error": "Thanh toán này đã bị hủy trước đó!"}, status=400)

        if instance.status == Payment.PaymentStatus.SUCCESS:
            return Response({"error": "Không thể hủy thanh toán đã thành công!"}, status=400)

        # Cập nhật trạng thái thanh toán
        instance.status = Payment.PaymentStatus.FAILED
        instance.save()

        logger.info(f"❌ Thanh toán {instance.id} bị hủy bởi admin!")

        return Response(
            {"message": "Thanh toán đã bị hủy thành công!", "payment": PaymentSerializer(instance).data},
            status=200
        )

