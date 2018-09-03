from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .models import Profile, Bonus, AuditLog
from .userforms import SignUpForm
from .models import account_activation_token
from django.core.mail import send_mail
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt


import logging
logger = logging.getLogger(__name__)

# @login_required
# @user_passes_test(lambda u: u.is_anonymous)
def index(request):
    print('access home')
    return render(request, 'home.html')


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            Profile.create(user, '', form.cleaned_data['rcode'])

            current_site = get_current_site(request)
            subject = 'Activate Your MySite Account'
            obj = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode("utf-8"),
                'token': account_activation_token.make_token(user)
            }
            message = render_to_string('account_activation_email.html',obj)

            msg = {'code': 200, 'msg': ''}
            logger.warning('message: {}, {}'.format(obj['uid'], obj['token']))
            try:
                send_mail(subject, message, 'git@youhub.cn' , [user.email], fail_silently=False)
            except:
                msg = {'code': 400, 'msg': 'failed to send email'}

            return render(request, 'account_activation_sent.html', {'user': user})
        else:
            return render(request, 'signup.html', {'form': form,})
    else:
        form = SignUpForm(initial={'rcode': request.GET.get('rcode', '')})
    return render(request, 'signup.html', {'form': form})

def add_bonus(users):
    # [t1, t2, t3]
    bonus = Bonus.objects.get(pk=1)
    if bonus.t1 == 0:
        return
    attr=['t1', 't2', 't3']
    for idx, user in enumerate(users):
        if user is None:
            continue
        b = getattr(bonus, attr[idx])
        user.profile.coins += b
        bonus.total_now += b

        if bonus.limit < bonus.total_now:
            bonus.t1 = 0
            bonus.t2 = 0
            bonus.t3 = 0
            bonus.last_update = timezone.now()
            bonus.save()
            user.profile.save()
            break
        else:
            pass
        bonus.save()
        user.profile.save()
        if idx == 1:
            a = AuditLog(ufrom=users[0].id, uto=users[1].id, level=1, coins=b)
            a.save()
        elif idx == 2:
            a = AuditLog(ufrom=users[0].id, uto=users[2].id, level=2, coins=b)
            a.save()

def activate(request, uidb64, token):
    # check password reset flag
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    flag_reset_password =False
    if token.startswith('FLPRE'):
        flag_reset_password = True
        token = token[5:]
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        if flag_reset_password:
            login(request, user)
            return render(request, 'password_reset.html', {'user': user})

        # add bonus to referrers
        ids, hashids = Profile.get_referres(user.profile.rcode)
        users = []
        # t3, t2, t1
        if ids != None:
            users = [User.objects.get(pk=id) if id!=0 else None for id in ids]
        users.append(user)
        # t1, t2, t3
        users.reverse()
        add_bonus(users)
        login(request, user)
        return redirect('base:index')
    else:
        return render(request, 'account_activation_invalid.html')

def get_rcode(request):

    ret = {'code': 400, 'rcode': 'no such user'}
    if request.user is not None and request.user.is_anonymous is False and request.user.is_active is True:
        rcode = request.user.profile.make_rcode()
        ret['rcode'] = rcode
        ret['code'] = 200
    return JsonResponse(ret, safe=False)

@csrf_exempt
def change_password(request):
    ret = {'code': 400, 'msg': 'no such user'}
    if request.user is not None and request.user.is_anonymous is False and request.user.is_active is True:
        pd = None
        if request.method == 'POST':
            pd = request.POST
        else:
            pd = request.GET
        old = pd.get('old', '')
        new = pd.get('new', '')
        if old == '' or new == '':
            ret['msg'] = 'invalid params'
        else:
            if not request.user.check_password(old):
                ret['msg'] = 'old password error'
            else:
                u = User.objects.get(pk = request.user.id)
                u.set_password(new)
                u.save()
                ret['code'] = 200
                ret['msg'] = 'ok'
                #update_session_auth_hash(request, request.user)
    return JsonResponse(ret, safe=False)

def resend_activation(request, name):
    ret = {'code': 400, 'msg': 'no such user or already activated'}
    # name or email
    u = None
    # if '@' not in name:
    #     u = User.objects.get(username=name)
    # else:
    u = User.objects.get(email=name)

    if u is not None and u.is_active is False:
        current_site = get_current_site(request)
        subject = 'Activate Your MySite Account'
        message = render_to_string('account_activation_email.html', {
            'user': u,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(u.id)).decode("utf-8"),
            'token': account_activation_token.make_token(u),
        })

        try:
            send_mail(subject, message, 'git@youhub.cn' , [u.email], fail_silently=False)
            ret = {'code': 200, 'msg': 'ok'}
        except:
            ret = {'code': 400, 'msg': 'failed to send email'}
    else:
        pass
    return JsonResponse(ret, safe=False)

def reset_password(request, name):
    ret = {'code': 400, 'msg': 'no such user or bad params'}
    u = User.objects.get(email = name)
    if u is None:
        pass
    else:
        current_site = get_current_site(request)
        subject = 'Reset Your Password Account'
        message = render_to_string('password_reset_email.html', {
            'user': u,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(u.id)).decode("utf-8"),
            'token': 'FLPRE'+account_activation_token.make_token(u),
        })
        try:
            send_mail(subject, message, 'git@youhub.cn' , [u.email], fail_silently=False)
            ret = {'code': 200, 'msg': 'ok'}
        except:
            ret = {'code': 400, 'msg': 'failed to send email'}

    return JsonResponse(ret, safe=False)

def password_reset(request):
    ret = {'code': 400, 'msg': 'no such user or bad params'}
    if request.method != 'POST':
        pass
    else:
        if request.user is not None and request.user.is_active:
            newpass = request.POST.get('newpass')
            if newpass is None or len(newpass) < 6:
                ret.msg = 'password format invalid'
                return JsonResponse(ret, safe=False)
            request.user.set_password(newpass)
            request.user.save()
            return JsonResponse({'code': 200, 'msg': 'ok'}, safe=False)

    return JsonResponse(ret, safe=False)

def get_bonus(request):
    ret = {'code': 400, 'msg': 'invalid request'}
    if request.user is not None and request.user.is_active:
        qs = Bonus.objects.all()
        qs = list(qs)
        if len(qs) != 1 :
            return JsonResponse(ret, safe=False)
        else:
            b = {'base': qs[0].as_dict(), 'b1_coins': 0, 'b2_conis': 0, 'b1_cnt':0, 'b2_cnt':0, 'b_total': request.user.profile.coins}
            b1 = AuditLog.objects.filter(uto=request.user.id).filter(level=1)
            for x in b1:
                b['b1_coins'] += x.coins
                b['b1_cnt'] += 1
            b2 = AuditLog.objects.filter(uto=request.user.id).filter(level=2)
            for x in b2:
                b['b2_conis'] += x.coins
                b['b2_cnt'] += 1

            return JsonResponse(b, safe=False)
    return JsonResponse(ret, safe=False)
