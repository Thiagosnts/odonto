# from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.messages import error, success

from apps.auth.models import Session
from .models import Treatment
from dentaladmin.utils import validate_form

Sessions = Session()
Treatments = Treatment()


def index(request, search=None):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa logar primeiro")
        return redirect('login')
    if auth_user['role'] != 'admin':
        error(request, "Você não tem permissão para este módulo")
        return redirect('/')
    if 'search' in request.GET:
        search = request.GET['search']
    treatments = Treatments.find_treatments(search)
    if treatments is None:
        return render(request, 'treatments/list.html', {'auth_user': auth_user, 'treatments': treatments})
    paginator = Paginator(treatments, 5)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return render(request, 'treatments/list.html', {'auth_user': auth_user, 'treatments': treatments, 'pages': pages})


def create_treatment(request):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa logar primeiro")
        return redirect('login')
    if auth_user['role'] != 'admin':
        error(request, "Você não tem permissão para este módulo")
        return redirect('/')
    if request.method == 'GET':
        return render(request, 'treatments/create.html', {'auth_user': auth_user})
    else:
        code = request.POST['code']
        name = request.POST['name']
        price = request.POST['price']
        form = validate_form(request.POST)
        if form is not True:
            error(request, "Há um problema com seus dados, favor verificar")
            return render(request, 'treatments/create.html',
                          {'auth_user': auth_user, 'code': code, 'name': name, 'price': price})
        result = Treatments.add_treatment(code, name, price)
        if result is not True:
            error(request, result)
            return render(request, 'treatments/create.html',
                          {'auth_user': auth_user, 'code': code, 'name': name, 'price': price})
        success(request, "Tratamento registrado com sucesso")
        response = redirect('treatments')
        return response


def edit_treatment(request, code):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa logar primeiro")
        return redirect('login')
    if auth_user['role'] != 'admin':
        error(request, "Você não tem permissão para este módulo")
        return redirect('/')
    if request.method == 'GET':
        treatment = Treatments.find_treatment(code)
        if treatment is None:
            error(request, "Esse tratamento não existe")
            return redirect('treatments')
        return render(request, 'treatments/edit.html', {'auth_user': auth_user, 'treatment': treatment})
    else:
        name = request.POST['name']
        price = request.POST['price']
        form = validate_form(request.POST)
        if form is not True:
            error(request, "Há um problema com seus dados, favor verificar")
            return redirect('edit_treatment', code=code)
        result = Treatments.edit_treatment(code, name, price)
        if result is not True:
            error(request, result)
            return redirect('edit_treatment', code=code)
        response = redirect('treatments')
        success(request, "Tratamento atualizado com sucesso")
        return response


def delete_treatment(request, code):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa logar primeiro")
        return redirect('login')
    if auth_user['role'] != 'admin':
        error(request, "Você não tem permissão para este módulo")
        return redirect('/')
    result = Treatments.delete_treatment(code)
    response = redirect('treatments')
    if result is not True:
        error(request, result)
        return response
    success(request, "Procedimento deletado com sucesso")
    return response
