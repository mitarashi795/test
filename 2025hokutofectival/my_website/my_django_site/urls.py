"""
URL configuration for my_django_site project.

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
from django.contrib import admin
from django.urls import path, include # include をインポート
from django.conf import settings # 追加
from django.conf.urls.static import static # 追加

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # ログイン・ログアウト用のURLをまとめて追加
    path('', include('accounts.urls')), # accountsアプリのURLを読み込む
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('polls/', include('polls.urls')), # ★pollsアプリのURLを読み込む
    path('schedule/', include('schedule.urls')), # ★この行を追加
]

# ★開発環境でメディアファイルを配信するための設定を追加
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)