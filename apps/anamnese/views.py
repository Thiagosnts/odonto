from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.messages import error, success
import json
from datetime import datetime


from apps.questions.models import Question
from apps.auth.models import Session
from apps.users.models import User
from apps.patients.models import Patient
from apps.treatment_sequences.models import Sequence
from apps.anamnese.models import Anamnese
from dentaladmin.utils import validate_form
from dentaladmin import utils

Sessions = Session()
Users = User()
Patients = Patient()
Sequences = Sequence()
Questions = Question()
Anamneses = Anamnese()


def montarDados(post):
    dict = post.dict()
    list = []

    for chave in dict.keys():
        list.append([chave,dict[chave]])    
    list.remove(list[0])   

    lista = {"lista":list}


    return str(lista)

def anamnese(request,token=None):
    tempoExpiracao=None;
    falha=False;

    try:
        dados = json.loads(utils.decode_ToBase64(token))
        tempoExpiracao = utils.get_interval_date(datetime.now(),dados.get('data_criacao'))
    except:
        falha=True;   

    if(falha or tempoExpiracao>=60):
        return render(request, 'erro.html')

    questions = Questions.list_questions()

    if questions is None:
        error(request, "Esse paciente não existe")
        return redirect('patients')

    if request.method == 'GET':

        return render(request, 'anamnese.html', {'questions':questions,'token':token})
    else:
        # name = request.POST['name']  
        # email = request.POST['email']  
        # phone = request.POST['phone'] 
        # role = request.POST['role']  
        # username = request.POST['username'] 
        # password = request.POST['password']  

        form = validate_form(request.POST)

        corpo = montarDados(request.POST)
        print("ok")

        #result = Anamneses.create_anamnese('cpf', 'pergunta', 'reposta')
        result = Patients.edit_patient_notes(dados.get('paciente'), corpo)

        success(request, "Registrado com sucesso")
        return redirect('questions', token=token)


        # if form is not True:
        #     error(request, "Tem algum problema em suas informações")
        #     return render(request, 'auth/signup.html',
        #                   {'name': name, 'email': email, 'phone': phone, 'role': role,
        #                    'username': username})
        # result = Users.add_user(name, email, phone, role, username, password)
        # if result is not True:
        #     error(request, result)
        #     return render(request, 'auth/signup.html')
        # success(request, "Registrado com sucesso")
        # response = redirect('login')
        # return response


# def login(request, token):
#     username=token
#     if request.method == 'GET':
#         return render(request, 'auth/login.html')
#     else:
#         if Sessions.validate_auth(request) is not None:
#             error(request, "Você ja esta logado")
#             return redirect('/')
#         username = request.POST['username']
#         password = request.POST['password']
#         user = Auths.login(username, password)
#         if user is None:
#             error(request, "Erro de autenticação de usuário")
#             return redirect('login')
#         session_id = Sessions.start_session(user["username"], user["role"])
#         response = redirect('/')
#         response.set_cookie(key="session", value=session_id)
#         success(request,None)
#         return response


# def logout(request):
#     response = redirect('login')
#     if "session" in request.COOKIES:
#         session_id = request.COOKIES['session']
#         Sessions.end_session(session_id)
#         response.delete_cookie('session')
#     success(request, "Logout feito com sucesso")
#     return response

#status 0=CANCELADO
#status 1=ABERTO
#status 2=ANDAMENTO
#status 3=FECHADO



# def dashboard(request):
#     auth_user = Sessions.validate_auth(request)
#     if auth_user is None:
#         error(request, "Você precisa logar primeiro")
#         return redirect('login')
#     if auth_user['role'] == 'doctor':
#         sequences = Sequences.find_sequences(None, auth_user['username'])
#     else:
#         sequences = Sequences.find_sequences(None)
#     users_count = 0
#     users = Users.find_users(None)
#     if users is not None:
#         users_count = users.count()
#     patients_count = 0
#     patients = Patients.find_patients(None)
#     if patients is not None:
#         patients_count = patients.count()
#     sequences_done = Sequences.report_sequences(None)
#     total = Sequences.report_sequences_total(None)
#     return render(request, 'auth/dashboard.html',
#                   {'auth_user': auth_user, 'users': users_count, 'patients': patients_count, 'sequences': sequences,
#                    'total': total,'sequences_done':sequences_done})
