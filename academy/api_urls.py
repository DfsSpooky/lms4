from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import api, api_auth, api_forum, api_payments

router = DefaultRouter()
router.register(r'courses', api.CourseViewSet)
router.register(r'progress', api.ProgressViewSet, basename='progress')
router.register(r'forum', api_forum.ForumViewSet)
router.register(r'notifications', api.NotificationViewSet, basename='notification')
router.register(r'installments', api_payments.InstallmentViewSet, basename='installment')

urlpatterns = [
    # Auth
    path('auth/login/', api_auth.LoginAPIView.as_view(), name='api_login'),
    path('auth/signup/', api_auth.SignupAPIView.as_view(), name='api_signup'),
    path('auth/password-reset/', api_auth.PasswordResetAPIView.as_view(), name='api_password_reset'),

    # Core
    path('me/', api.current_user, name='api_me'),
    path('my-courses/', api.MyCoursesViewSet.as_view({'get': 'list'}), name='api_my_courses'),

    # Router
    path('', include(router.urls)),
]
