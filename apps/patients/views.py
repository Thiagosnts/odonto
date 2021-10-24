# from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.messages import error, success

from apps.anamnese.models import Question

from apps.auth.models import Session
from apps.treatment_sequences.models import Sequence
from .models import Patient
from dentaladmin.utils import validate_form

Sessions = Session()
Sequences = Sequence()
Patients = Patient()
Questions = Question()




def index(request, search=None):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if 'search' in request.GET:
        search = request.GET['search']
    patients = Patients.find_patients(search)
    if patients is None:
        return render(request, 'patients/list.html', {'auth_user': auth_user, 'patients': patients})
    paginator = Paginator(patients, 5)
    page = request.GET.get('page')
    try:
        pages = paginator.page(page)
    except PageNotAnInteger:
        pages = paginator.page(1)
    except EmptyPage:
        pages = paginator.page(paginator.num_pages)
    return render(request, 'patients/list.html', {'auth_user': auth_user, 'patients': patients, 'pages': pages})


def create_patient(request):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'GET':
        return render(request, 'patients/create.html', {'auth_user': auth_user})
    else:
        dni = request.POST['dni']
        name = request.POST['name']
        date_of_birth = request.POST['date_of_birth']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        visit_reason = request.POST['visit_reason']
        form = validate_form(request.POST)
        if form is not True:
            error(request, "Existe um problema com as suas informações, Favor Verificar")
            return render(request, 'patients/create.html',
                          {'auth_user': auth_user, 'dni': dni, 'name': name, 'date_of_birth': date_of_birth,
                           'email': email, 'phone': phone, 'address': address, 'visit_reason': visit_reason})
        result = Patients.add_patient(dni, name, date_of_birth, email, phone, address, visit_reason)
        if result is not True:
            error(request, result)
            return render(request, 'patients/create.html',
                          {'auth_user': auth_user, 'dni': dni, 'name': name, 'date_of_birth': date_of_birth,
                           'email': email, 'phone': phone, 'address': address, 'visit_reason': visit_reason})
        success(request, "Paciente Registrado com Sucesso")
        response = redirect('patients')
        return response


def edit_patient(request, dni):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'GET':
        patient = Patients.find_patient(dni)
        if patient is None:
            error(request, "O paciente não Existe")
            return redirect('patients')
        return render(request, 'patients/edit.html', {'auth_user': auth_user, 'patient': patient})
    else:
        name = request.POST['name']
        date_of_birth = request.POST['date_of_birth']
        email = request.POST['email']
        phone = request.POST['phone']
        address = request.POST['address']
        visit_reason = request.POST['visit_reason']
        form = validate_form(request.POST)
        if form is not True:
            error(request, "Existe um problema com as suas informações, Favor Verificar")
            return redirect('edit_patient', dni=dni)
        result = Patients.edit_patient(dni, name, date_of_birth, email, phone, address, visit_reason)
        if result is not True:
            error(request, result)
            return redirect('edit_patient', dni=dni)
        response = redirect('patients')
        success(request, "Paciente atualizado com sucesso")
        return response


def check_patient(request, dni):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'GET':
        patient = Patients.find_patient(dni)
        diagnostics = Patients.find_diagnostics(dni)
        questions = Questions.list_questions()
        if patient is None:
            error(request, "Esse paciente não existe")
            return redirect('patients')
        return render(request, 'patients/check.html',
                      {'auth_user': auth_user, 'patient': patient, 'diagnostics': diagnostics, 'questions':questions})
    # else:
    #     # notes = request.POST['notes']
    #     # question = request.POST['question']

    #     form = validate_form(request.POST)
    #     if form is not True:
    #         error(request, "Existe um problema com as suas informações, Favor Verificar")
    #         return redirect('check_patient', dni=dni)

    #     # result = Questions.add_question(question)
        
    #     if result is not True:
    #         error(request, result)
    #     # else:
    #     #     success(request, "Prontuário atualizado com sucesso")
    #     else:
    #         success(request, "Pergunta adicionada com sucesso")
    #     return redirect('check_patient', dni=dni)


def create_diagnostic(request, dni):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'POST':
        date = request.POST['date']
        doctor = request.POST['doctor']
        tooths = request.POST['tooths']
        diagnostic = request.POST['diagnostic']
        form = validate_form(request.POST)
        if form is not True:
            error(request, "Existe um problema com as suas informações, Favor Verificar")
            return redirect('check_patient', dni=dni)
        result = Patients.add_diagnostic(dni, date, doctor, tooths, diagnostic)
        if result is not True:
            error(request, result)
        else:
            success(request, "Paciente atualizado com sucesso")
        return redirect('check_patient', dni=dni)


def delete_diagnostic(request, dni, code):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'GET':
        result = Patients.delete_diagnostic(dni, code)
        if result is not True:
            error(request, result)
        else:
            success(request, "Paciente atualizado com sucesso")
        return redirect('check_patient', dni=dni)


def delete_patient(request, dni):
    if Sessions.validate_auth(request) is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    result = Patients.delete_patient(dni)
    Sequences.cancel_sequences_from_patient(dni)
    response = redirect('patients')
    if result is not True:
        error(request, result)
        return response
    success(request, "Paciente deletado com sucesso")
    return response

def create_question(request, dni):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'POST':
        question = request.POST['question']
        form = validate_form(request.POST)
        if form is not True:
            error(request, "Existe um problema com as suas informações, Favor Verificar")
            return redirect('check_patient', dni=dni)

        result = Questions.add_question(question)   

        if result is not True:
            error(request, result)
        else:
            success(request, "Pergunta adicionada com sucesso")
        return redirect('check_patient', dni=dni)


def delete_question(request,dni, code):
    if Sessions.validate_auth(request) is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    result = Patients.delete_question(code)
    # Sequences.cancel_sequences_from_patient(dni)
    response = redirect('patients')
    if result is not True:
        error(request, result)
        return response
    success(request, "Pergunta deletada com sucesso")
    return response
