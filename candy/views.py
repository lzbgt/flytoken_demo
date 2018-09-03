from django.http import HttpResponse, HttpResponseRedirect
from .models import Token
from django.views import generic
from django.urls import reverse
from django.http import JsonResponse
from django.core import serializers
import sys
import json

ERROR_401 = {'code': 401, 'message': 'object not found'}


def index(request):
    ret = {}
    try:
        tokens = [token.as_dict() for token in  Token.objects.order_by('-create_time')]
    except :
        tokens = ERROR_401
        tokens['message'] = str(sys.exc_info()[0])
    print(tokens)

    return JsonResponse(tokens, safe=False)


def detail(request, id):
    try:
        token = Token.objects.get(pk=id).as_dict()
    except:
        token = ERROR_401
        token['message'] = str(sys.exc_info()[0])

    return JsonResponse(token, safe=False)
