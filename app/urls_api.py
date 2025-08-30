from django.urls import path
from rest_framework.routers import DefaultRouter
from .api_views import ProductViewSet
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register('products', ProductViewSet, basename='api-product')

urlpatterns = router.urls

# urlpatterns += [
#     path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
# ]
