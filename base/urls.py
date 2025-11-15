"""
URL configuration for base project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf.urls.static import static
from decouple import config

from .views import IndexPageView

template_urls = [
    path("", IndexPageView.as_view(), name="index"),
]

swagger_urls = [
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(), name='redoc'),
]

v1_apis = [
    path("v1/api/auth/", include("apis.v1.auth.urls", namespace="v1_auth")),
]

urlpatterns = [
    path('admin/', admin.site.urls),
] + swagger_urls + v1_apis + template_urls

SHOW_DEBUGGER_TOOLBAR = config("SHOW_DEBUGGER_TOOLBAR", cast=bool, default=True)
if SHOW_DEBUGGER_TOOLBAR:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()

DEBUG = config("DEBUG", cast=bool, default=True)
if DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

USE_SPECTACULAR_EXTRAS_SETTINGS = config("USE_SPECTACULAR_EXTRAS_SETTINGS", cast=bool, default=True)
if USE_SPECTACULAR_EXTRAS_SETTINGS:
    from drf_spectacular_extras.views import SpectacularScalarView
    urlpatterns += [
        path('api/schema/scalar/', SpectacularScalarView.as_view(url_name='schema'), name='scalar'),
    ]
