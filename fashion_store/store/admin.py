from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from .models import Category, Product, Review, Cart, CartItem, Order, OrderItem, Payment, Banner

# ✅ Lấy model User động
User = get_user_model()

# ✅ Kiểm tra nếu chưa đăng ký thì mới đăng ký
if not admin.site.is_registered(User):
    admin.site.register(User, UserAdmin)

# Đăng ký các model bình thường
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)

# Kiểm tra nếu model đã được đăng ký, sau đó mới hủy đăng ký
if admin.site.is_registered(Review):
    admin.site.unregister(Review)

if admin.site.is_registered(Banner):
    admin.site.unregister(Banner)

# Tạo class để ẩn model khỏi Sidebar nhưng vẫn truy cập được qua URL
class HiddenAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {}  # Ẩn khỏi sidebar nhưng vẫn có thể truy cập qua URL

# Đăng ký lại Review & Banner nhưng không hiển thị trên Sidebar
admin.site.register(Review, HiddenAdmin)
admin.site.register(Banner, HiddenAdmin)

