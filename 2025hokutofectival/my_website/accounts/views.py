# accounts/views.py (全体を置き換え)
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
import json

from .forms import CustomLoginForm
from .models import LoginRequest

def custom_login(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        form = CustomLoginForm(data)
        if form.is_valid():
            role = form.cleaned_data['role']
            # ★「クラス展示関係者」も自動承認の対象に追加
            is_approved = role in ['教員', '部活動関係者', 'クラス展示関係者']
            
            login_request = LoginRequest.objects.create(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                role=role,
                committee=form.cleaned_data.get('committee'),
                club=form.cleaned_data.get('club'),
                class_exhibit=form.cleaned_data.get('class_exhibit'),
                is_approved=is_approved
            )
            
            # ... (以降のセッション保存などの処理は変更なし) ...
            my_account_ids = request.session.get('my_account_ids', [])
            my_account_ids.append(login_request.id)
            request.session['my_account_ids'] = my_account_ids
            request.session['login_request_id'] = login_request.id
            request.session['user_role'] = login_request.role
            
            redirect_url = '/dashboard/' if is_approved else '/wait_for_approval/'
            return JsonResponse({'success': True, 'redirect_url': redirect_url})
        else:
            return JsonResponse({'success': False, 'error': '入力内容に誤りがあります。'})
    return JsonResponse({'success': False, 'error': '不正なリクエストです。'})

# --- ログアウト処理 (全アカウント情報をクリア) ---
def custom_logout(request):
    # セッションからアカウント関連の情報をすべて削除
    for key in ['login_request_id', 'user_role', 'my_account_ids']:
        if key in request.session:
            del request.session[key]
    return redirect('landing')

# --- ★新規追加：アカウント一覧ページ ---
class AccountListView(View):
    def get(self, request, *args, **kwargs):
        my_account_ids = request.session.get('my_account_ids', [])
        if not my_account_ids:
            return redirect('landing')
            
        my_accounts = LoginRequest.objects.filter(id__in=my_account_ids).order_by('-timestamp')
        
        context = {
            'my_accounts': my_accounts,
        }
        return render(request, 'account_list.html', context)

# --- ★新規追加：アカウント切り替え処理 ---
def switch_account(request, pk):
    my_account_ids = request.session.get('my_account_ids', [])
    
    # セキュリティチェック：自分のアカウントリストに含まれるIDにしか切り替えられない
    if pk in my_account_ids:
        account_to_switch = get_object_or_404(LoginRequest, pk=pk)
        request.session['login_request_id'] = account_to_switch.id
        request.session['user_role'] = account_to_switch.role
        
        # 承認状態に応じてダッシュボードか承認待ちページへ
        if account_to_switch.is_approved:
            return redirect('dashboard')
        else:
            return redirect('wait_for_approval')
            
    return redirect('landing') # 不正なアクセスはトップへ

# --- 既存のビュー (変更なし) ---
class WaitForApprovalView(View):
    def get(self, request, *args, **kwargs):
        login_request_id = request.session.get('login_request_id')
        if not login_request_id: return redirect('landing')
        login_request = get_object_or_404(LoginRequest, id=login_request_id)
        if login_request.is_approved: return redirect('dashboard')
        return render(request, 'wait_for_approval.html', {'login_request': login_request})

class ApprovalListView(View):
    def get(self, request, *args, **kwargs):
        login_request_id = request.session.get('login_request_id')
        if not login_request_id: return redirect('landing')
        current_user = get_object_or_404(LoginRequest, id=login_request_id)
        pending_requests = []
        if current_user.role == '教員':
            pending_requests = LoginRequest.objects.filter(role='実行委員長', is_approved=False).order_by('timestamp')
        elif current_user.role == '実行委員長':
            pending_requests = LoginRequest.objects.filter(role='委員長', is_approved=False).order_by('timestamp')
        context = {'current_user': current_user, 'pending_requests': pending_requests}
        return render(request, 'approval_list.html', context)

def approve_request(request, pk):
    request_to_approve = get_object_or_404(LoginRequest, pk=pk)
    request_to_approve.is_approved = True
    request_to_approve.save()
    return redirect('approval_list')
    
class LandingPageView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'landing.html')

class DashboardView(View):
    def get(self, request, *args, **kwargs):
        login_request_id = request.session.get('login_request_id')
        if not login_request_id: return redirect('landing')
        login_request = get_object_or_404(LoginRequest, id=login_request_id)
        if not login_request.is_approved: return redirect('wait_for_approval')
        return render(request, 'dashboard.html', {'login_request': login_request})