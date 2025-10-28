# accounts/urls.py (修正)
from django.urls import path
from . import views

urlpatterns = [
    path('', views.LandingPageView.as_view(), name='landing'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('logout/', views.custom_logout, name='logout'),
    path('ajax/login/', views.custom_login, name='ajax_login'),
    
    # 新しく追加するURL
    path('wait_for_approval/', views.WaitForApprovalView.as_view(), name='wait_for_approval'),
    path('approval/', views.ApprovalListView.as_view(), name='approval_list'),
    path('approve/<int:pk>/', views.approve_request, name='approve_request'),
    path('accounts/', views.AccountListView.as_view(), name='account_list'),
    path('switch_account/<int:pk>/', views.switch_account, name='switch_account'),
]