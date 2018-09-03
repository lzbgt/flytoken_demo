from django.urls import path

from . import views

from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

app_name = 'base'
urlpatterns = [
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': 'base:index'}, name='logout'),
    url(r'^$', views.index, name='index'),
    url(r'^rcode/$', views.get_rcode, name='rcode'),
    path('accounts/profile/',  RedirectView.as_view(url='/', permanent=False), name='profile'),
    url(r'^signup/$', views.signup, name='signup'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('change_password', views.change_password, name='change_password'),
    path('resend_activation/<name>/', views.resend_activation, name='resend_activation'),
    path('reset_password/<name>/', views.reset_password, name='reset_password'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('bonus/', views.get_bonus, name='get_bonus'),
]