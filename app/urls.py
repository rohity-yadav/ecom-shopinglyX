from django.urls import path, include
from app import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from .forms import LoginForm, MypasswordChangeForm, MyPasswordReset, MySetPasswordForm

urlpatterns = [
    # HTML Views...
    path('', views.ProdectHomeView.as_view(), name='home'),
    path('product-detail/<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('add-to-cart/', views.add_to_cart, name='add-to-cart'),
    path('cart/', views.show_cart, name='showcart'),
    path('pluscart/', views.plus_cart, name='plus-cart'),
    path('minuscart/', views.minus_cart, name='minus-cart'),
    path('removecart/', views.remove_cart, name='remove-cart'),
    path('paymentdone/', views.payment_done, name='paymentdone'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('buy-now/<int:pk>/', views.buy_now, name='buy-now'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('address/', views.address, name='address'),
    path('orders/', views.orders, name='orders'),
    path('search/', views.search_view, name='search'),
    path('mobile/', views.mobile, name='mobile'),
    path('mobile/<slug:data>', views.mobile, name='mobiledata'),
    path('watch/', views.watch, name='watch'),
    path('watch/<slug:data>', views.watch, name='watchdata'),

    path('topwear/', views.topwear, name='topwear'),
    path('bottomwear/', views.bottomwear, name='bottomwear'),
    
    # Auth Views...
    path('accounts/login/', auth_views.LoginView.as_view(template_name='app/login.html', authentication_form=LoginForm), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('passwordchange/', auth_views.PasswordChangeView.as_view(template_name='app/passwordchange.html', form_class=MypasswordChangeForm, success_url='/passwordchangedone/'), name='passwordchange'),
    path('passwordchangedone/', auth_views.PasswordChangeDoneView.as_view(template_name='app/passwordchangedone.html'), name='passwordchangedone'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='app/password_reset.html', form_class=MyPasswordReset), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'), name='password_reset_done'),
    path('password-reset_confirm/<uidb64>/<token>', auth_views.PasswordResetConfirmView.as_view(template_name='app/password_confirm.html', form_class=MySetPasswordForm), name='password_reset_confirm'),
    path('password-reset-complet/', auth_views.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'), name='password_reset_complete'),
    path('registration/', views.CustomerRegistration.as_view(), name='customerregistration'),

    # Checkout
    path('checkout/', views.checkout, name='checkout'),

    # Admin pannel urls
    path('admin-login/', views.admin_login, name='adminlogin'),
    path("admin-logout/", views.admin_logout, name="admin_logout"),
    path('dashbord/', views.dashbord, name='dashbord'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/edit/<int:id>/', views.edit_product, name='edit_product'),
    path('products/delete/<int:id>/', views.delete_product, name='delete_product'),

    # ✅ API URLs वेगळ्या file मधून include केले
    path('api/', include('app.urls_api')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
 