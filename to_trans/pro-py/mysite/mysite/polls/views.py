from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def hello(request):
    """

    :param request:
    :return:
    """
    return HttpResponse("hello, world")