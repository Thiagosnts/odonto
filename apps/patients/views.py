# from django.http import HttpResponse
from django.core.mail import BadHeaderError, EmailMultiAlternatives
from django.template.loader import get_template
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, redirect
from django.contrib.messages import error, success
from datetime import datetime
from apps.anamnese.views import anamnese
from dentaladmin import utils



from apps.questions.models import Question
from apps.anamnese.models import Anamnese
from apps.auth.models import Session
from apps.treatment_sequences.models import Sequence
from .models import Patient
from dentaladmin.utils import validate_form

Sessions = Session()
Sequences = Sequence()
Patients = Patient()
Questions = Question()
Anamneses = Anamnese()



def invoice_anamnese(request, cpf, link):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa logar primeiro")
        return redirect('login')
    # if request.method == 'GET':
        #sequence = Sequences.find_sequence(code)
        #sequence_treatments = Sequences.find_sequence_treatments(code)
        # if sequence is None:
        #     error(request, "Este prontuário não existe")
        #     return redirect('sequences')
        # return render(request, 'sequences/invoice.html',
        #               {'auth_user': auth_user, 'sequence': sequence, 'sequence_treatments': sequence_treatments})
    # if request.method == 'POST':
    if True:
        # sequence = Sequences.find_sequence(code)
        # sequence_treatments = Sequences.find_sequence_treatments(code)
        patient = Patients.get_patient_by_cpf(cpf)
        try:
            # plaintext = get_template('anamnese/emails/email.txt')
            htmly = get_template('emails/email.html')

            # data = Context({'patient': patient, 'sequence': sequence, 'sequence_treatments': sequence_treatments})

            data = {'patient': patient, 'link':link}

            subject, from_email, to = 'Formulário Anamnese', 'no-reply@leadodonto.com', patient['email']
            # text_content = plaintext.render(data)
            html_content = htmly.render(data)
            # msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
            msg = EmailMultiAlternatives(subject, html_content , from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except BadHeaderError:
            error(request, "Anamnese não enviada")
            return redirect('check_patient', cpf=cpf)
     




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
        cpf = request.POST['cpf']
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
                          {'auth_user': auth_user, 'cpf': cpf, 'name': name, 'date_of_birth': date_of_birth,
                           'email': email, 'phone': phone, 'address': address, 'visit_reason': visit_reason})
        result = Patients.add_patient(cpf, name, date_of_birth, email, phone, address, visit_reason)
        if result is not True:
            error(request, result)
            return render(request, 'patients/create.html',
                          {'auth_user': auth_user, 'cpf': cpf, 'name': name, 'date_of_birth': date_of_birth,
                           'email': email, 'phone': phone, 'address': address, 'visit_reason': visit_reason})
        success(request, "Paciente Registrado com Sucesso")
        response = redirect('patients')
        return response


def edit_patient(request, cpf):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'GET':
        patient = Patients.find_patient(cpf)
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
            return redirect('edit_patient', cpf=cpf)
        result = Patients.edit_patient(cpf, name, date_of_birth, email, phone, address, visit_reason)
        if result is not True:
            error(request, result)
            return redirect('edit_patient', cpf=cpf)
        response = redirect('patients')
        success(request, "Paciente atualizado com sucesso")
        return response


def check_patient(request, cpf):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'GET':
        patient = Patients.find_patient(cpf)
        diagnostics = Patients.find_diagnostics(cpf)

        questions = Questions.list_questions()
        
        anamnese = Anamneses.find_anamnese(cpf)

        if patient is None:
            error(request, "Esse paciente não existe")
            return redirect('patients')
        return render(request, 'patients/check.html',
            {'auth_user': auth_user, 'patient': patient, 'diagnostics': diagnostics,'questions':questions, 'anamnese':anamnese})
    
    token = gerar_token(cpf)
    url = f'http://localhost:8000/anamnese/{token}'

    form = validate_form(request.POST)
    if form is not True:
        error(request, "Existe um problema com as suas informações, Favor Verificar")
        return redirect('check_patient', cpf=cpf)
    
    if list(request.POST.values())[1]=="preencher":
        return redirect(url)
    else:
        invoice_anamnese(request, cpf, url)
        success(request, "Anamnese enviada para o email do Paciente")
        return redirect('check_patient', cpf=cpf)


def create_diagnostic(request, cpf):
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
            return redirect('check_patient', cpf=cpf)
        result = Patients.add_diagnostic(cpf, date, doctor, tooths, diagnostic)
        if result is not True:
            error(request, result)
        else:
            success(request, "Paciente atualizado com sucesso")
        return redirect('check_patient', cpf=cpf)


def delete_diagnostic(request, cpf, code):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'GET':
        result = Patients.delete_diagnostic(cpf, code)
        if result is not True:
            error(request, result)
        else:
            success(request, "Paciente atualizado com sucesso")
        return redirect('check_patient', cpf=cpf)


def delete_patient(request, cpf):
    if Sessions.validate_auth(request) is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    result = Patients.delete_patient(cpf)
    Sequences.cancel_sequences_from_patient(cpf)
    response = redirect('check_patient')
    if result is not True:
        error(request, result)
        return response
    success(request, "Paciente deletado com sucesso")
    return response

def create_question(request, cpf):
    auth_user = Sessions.validate_auth(request)
    if auth_user is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    if request.method == 'POST':
        question = request.POST['question']
        form = validate_form(request.POST)
        if form is not True:
            error(request, "Existe um problema com as suas informações, Favor Verificar")
            return redirect('check_patient', cpf=cpf)

        result = Questions.create_question(question)   

        if result is not True:
            error(request, result)
        else:
            success(request, "Pergunta adicionada com sucesso")
        return redirect('check_anamnese', cpf=cpf)


def delete_question(request,cpf, code):
    if Sessions.validate_auth(request) is None:
        error(request, "Você precisa Logar Primeiro")
        return redirect('login')
    result = Questions.delete_question(code)
    # Sequences.cancel_sequences_from_patient(cpf)
    response = redirect('check_anamnese', cpf=cpf)
    if result is not True:
        error(request, result)
        return response
    success(request, "Pergunta deletada com sucesso")
    return response

def gerar_token(cpf):
    dataAtual = str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    corpo = {'acesso': 'garantido', 'data_criacao': dataAtual, 'paciente': cpf}
    token = utils.encode_ToBase64(str(corpo)).replace("=", "")
    return token
    

