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

from apps.payments.views import MembershipPaymentModelViewSet
from apps.profiles.views import UserModelViewSet

router = routers.SimpleRouter(trailing_slash=False)
router.register(r'users', UserModelViewSet, basename='users')

# Nested routes
membership_payments_router = routers.NestedSimpleRouter(router, r'users', lookup='user')
membership_payments_router.register(r'membership_payments', MembershipPaymentModelViewSet,
                                    basename='membership-payments')

urlpatterns = [
    path('staff/', admin.site.urls),
    path('', include('apps.profiles.urls', namespace='profiles_urls')),
]

urlpatterns += router.urls
urlpatterns += membership_payments_router.urls
