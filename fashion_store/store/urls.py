from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterView, LoginView, ProductListCreateView, ProductDetailView, CreateOrderView, 
    UserOrderListView, OrderDetailView, CancelOrderView, DeleteOrderView, 
    AddToCartView, UpdateCartItemView, RemoveFromCartView, CategoryViewSet, PaymentView,
    UserPaymentListView, PaymentDetailView, CancelPaymentView, home_view, contact_view,
    login_view, register_view, productall_view, profile_view, product_detail, UserInfoView, cart_view, CartDetailView ,
    pay_view, sales_view
)

# ✅ Router xử lý API cho danh mục sản phẩm
router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')

urlpatterns = [
    # 🌐 Giao diện người dùng
    path('', home_view, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('profile/', profile_view, name='profile'),
    path('productall/', productall_view, name='productall'),
    path('products/<int:pk>/', product_detail, name='product-detail'),
    path('contact/', contact_view, name='contact'),
    path('pay/', pay_view  , name='pay'),
    path('best_sales/', sales_view  , name='best_sales'),
    path('cart/', cart_view, name='cart'),

    # 🔗 API Người dùng
    path('api/auth/user/', UserInfoView.as_view(), name='user-info'),
    path('api/auth/register/', RegisterView.as_view(), name='api_register'),
    path('api/auth/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # 🔗 API Sản phẩm
    path('api/products/', ProductListCreateView.as_view(), name='product-list'),
    path('api/products/<int:pk>/', ProductDetailView.as_view(), name='product-detail-api'),

    # 🔗 API Giỏ hàng (các thao tác riêng)
    path('api/cart/', CartDetailView.as_view(), name='cart-detail'),
    path('api/cart/add/', AddToCartView.as_view(), name='cart-add'),
    path('api/cart/update/<int:pk>/', UpdateCartItemView.as_view(), name='cart-update'),
    path('api/cart/remove/<int:pk>/', RemoveFromCartView.as_view(), name='cart-remove'),

    # ✅ Đăng ký router để xử lý API danh mục (và nếu có ViewSet khác được đăng ký)
    path('api/', include(router.urls)),

    # 🔗 API đơn hàng
    path('api/orders/', UserOrderListView.as_view(), name='order-list'),
    path('api/orders/create/', CreateOrderView.as_view(), name='create-order'),
    path('api/orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('api/orders/cancel/<int:pk>/', CancelOrderView.as_view(), name='cancel-order'),
    path("api/orders/delete/<int:pk>/", DeleteOrderView.as_view(), name="delete-order"),
    path('api/order/update-cart/', UpdateCartItemView.as_view(), name='update_cart'),

    # 🔗 API thanh toán
    path("api/orders/payment/", PaymentView.as_view(), name="order-payment"),
    path("api/orders/payments/", UserPaymentListView.as_view(), name="user-payment-list"),
    path("api/orders/payment/<int:pk>/", PaymentDetailView.as_view(), name="payment-detail"),
    path("api/orders/payment/cancel/<int:pk>/", CancelPaymentView.as_view(), name="cancel-payment"),
]
