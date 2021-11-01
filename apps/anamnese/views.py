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


def montarDados(cpf, post):
    dict = post.dict()
    list = []

    for chave in dict.keys():
        list.append({"cpf": cpf,"pergunta": chave, "resposta": dict[chave]})

    list.remove(list[0])   
    return list


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
        corpo = montarDados(dados.get('paciente'),request.POST)

        Anamneses.delete_anamnese(dados.get('paciente'))
        Anamneses.create_anamnese(corpo)

        success(request, "Registrado com sucesso")
        return render(request, 'sucesso.html')



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
