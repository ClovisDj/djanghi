"""apps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework_nested import routers

from apps.payments.views import MembershipPaymentModelViewSet, MembershipPaymentStatusModelViewSet
from apps.profiles.views import UserModelViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserModelViewSet, basename='users')

# Nested routes
users_nested_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
users_nested_router.register(r'membership_payments', MembershipPaymentModelViewSet, basename='membership-payments')
users_nested_router.register(r'payments_status', MembershipPaymentStatusModelViewSet,
                             basename='membership-payments-status')

urlpatterns = [
    path('staff/', admin.site.urls),
    path('', include('apps.profiles.urls', namespace='profiles_urls')),
    path('', include('apps.associations.urls', namespace='associations_urls')),
    path('', include('apps.payments.urls', namespace='payments_urls')),
]

urlpatterns += router.urls
urlpatterns += users_nested_router.urls
