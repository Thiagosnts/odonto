from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.messages import error, success
import json
from datetime import datetime


from apps.anamnese.models import Question
from apps.auth.models import Session
from apps.users.models import User
from apps.patients.models import Patient
from apps.treatment_sequences.models import Sequence
from dentaladmin.utils import validate_form
from dentaladmin import utils

Sessions = Session()
Users = User()
Patients = Patient()
Sequences = Sequence()
Questions = Question()


