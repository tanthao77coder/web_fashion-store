# Generated by Django 4.2 on 2025-03-14 20:03

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('so_dien_thoai', models.CharField(max_length=20, null=True, unique=True)),
                ('dia_chi', models.TextField(blank=True, null=True)),
                ('vai_tro', models.CharField(choices=[('admin', 'Admin'), ('khach_hang', 'Khách hàng')], default='khach_hang', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, related_name='+', to='auth.group')),
                ('user_permissions', models.ManyToManyField(blank=True, related_name='+', to='auth.permission')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tieu_de', models.CharField(max_length=255)),
                ('hinh_anh', models.URLField()),
                ('lien_ket', models.URLField(blank=True, null=True)),
                ('ngay_tao', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ngay_tao', models.DateTimeField(auto_now_add=True)),
                ('nguoi_dung', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ten_danh_muc', models.CharField(max_length=255, unique=True)),
                ('mo_ta', models.TextField(blank=True, null=True)),
                ('ngay_tao', models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tong_tien', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('phuong_thuc_tt', models.CharField(choices=[('cod', 'Thanh toán khi nhận hàng'), ('online', 'Thanh toán Online')], default='cod', max_length=10)),
                ('phuong_thuc_online', models.CharField(blank=True, choices=[('momo', 'MoMo'), ('zalopay', 'ZaloPay'), ('vnpay', 'VNPay')], max_length=10, null=True)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('nguoi_dung', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ten_san_pham', models.CharField(max_length=255)),
                ('mo_ta', models.TextField()),
                ('gia', models.DecimalField(decimal_places=0, max_digits=10)),
                ('giam_gia', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('so_luong', models.IntegerField(default=0)),
                ('so_luong_ban', models.IntegerField(default=0)),
                ('thuong_hieu', models.CharField(blank=True, max_length=50, null=True)),
                ('kich_co', models.CharField(choices=[('36', '36'), ('37', '37'), ('38', '38'), ('39', '39'), ('40', '40'), ('41', '41'), ('42', '42'), ('43', '43'), ('44', '44'), ('45', '45')], max_length=10)),
                ('mau_sac', models.CharField(max_length=50)),
                ('chat_lieu', models.CharField(blank=True, max_length=100, null=True)),
                ('gioi_tinh', models.CharField(choices=[('Nam', 'Nam'), ('Nữ', 'Nữ'), ('Unisex', 'Unisex')], default='Unisex', max_length=10)),
                ('hinh_anh', models.URLField(blank=True, max_length=255, null=True)),
                ('ngay_tao', models.DateTimeField(auto_now_add=True)),
                ('danh_muc', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='store.category')),
            ],
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('danh_gia', models.IntegerField(choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')])),
                ('binh_luan', models.TextField()),
                ('ngay_tao', models.DateTimeField(auto_now_add=True)),
                ('nguoi_dung', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('san_pham', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('payment_method', models.CharField(choices=[('VNPay', 'VNPay'), ('MoMo', 'MoMo'), ('COD', 'Thanh toán khi nhận hàng')], max_length=20)),
                ('status', models.CharField(choices=[('Cho_xac_nhan', 'Chờ xác nhận'), ('Thanh_cong', 'Thành công'), ('That_bai', 'Thất bại')], default='Cho_xac_nhan', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='payment', to='store.order')),
            ],
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('so_luong', models.PositiveIntegerField()),
                ('gia', models.DecimalField(decimal_places=2, max_digits=10)),
                ('don_hang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_items', to='store.order')),
                ('san_pham', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
        migrations.CreateModel(
            name='CartItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('so_luong', models.IntegerField(default=1)),
                ('gia_sau_giam', models.DecimalField(decimal_places=0, default=0, max_digits=10)),
                ('gio_hang', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='store.cart')),
                ('san_pham', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='store.product')),
            ],
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['order'], name='store_payme_order_i_56dfe1_idx'),
        ),
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(fields=['transaction_id'], name='store_payme_transac_3bbf2d_idx'),
        ),
    ]
