from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Patient:
    def __init__(self):
        self.db = database
        self.patients = self.db.patients

    def find_patients(self, search, status=1):
        query = {'status': status}
        if search is not None:
            query = {'status': status, '$or': [
                {'cpf': {'$regex': search, '$options': 'i'}},
                {'name': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
                {'phone': {'$regex': search, '$options': 'i'}}
            ]}
        patients = self.patients.find(query)
        count = patients.count()
        if count > 0:
            return patients
        return None

    def find_patient(self, cpf, status=1):
        patient = self.patients.find_one({'cpf': cpf, 'status': status})
        if not patient:
            return None
        return patient

    def add_patient(self, cpf, name, date_of_birth, email, phone, address, visit_reason, status=1):
        patient_exist = self.patients.find_one({'cpf': cpf, 'status': status})
        email_exist = self.patients.find_one({'email': email, 'status': status})
        if patient_exist:
            return "Oops, cpf já existente"
        if email_exist:
            return "Oops, email já existente"
        patient = {'cpf': cpf, 'name': name, 'date_of_birth': date_of_birth, 'email': email, 'phone': phone,
                   'address': address, 'visit_reason': visit_reason, 'status': status}
        try:
            self.patients.insert_one(patient)
        except errors.OperationFailure:
            return "oops, mongo error"
        return True

    def edit_patient(self, cpf, name, date_of_birth, email, phone, address, visit_reason):
        patient = self.find_patient(cpf)
        if patient is None:
            return "Paciente não encontrado"
        try:
            self.patients.update_one({'cpf': cpf}, {
                '$set': {'name': name, 'date_of_birth': date_of_birth, 'email': email, 'phone': phone,
                         'address': address, 'visit_reason': visit_reason}})
        except errors.OperationFailure:
            return "Oops, Paciente não atualizado"
        return True

    def edit_patient_notes(self, cpf, notes):
        patient = self.find_patient(cpf)
        if patient is None:
            return "Paciente não encontrado"
        try:
            self.patients.update_one({'cpf': cpf}, {'$set': {'notes': notes}})
        except errors.OperationFailure:
            return "Oops, Paciente não atualizado"
        return True

    def find_diagnostics(self, cpf, status=1):
        cursor = self.patients.aggregate([
            {'$match': {'cpf': cpf, 'status': status}},
            {'$unwind': "$clinic_history"},
            {"$project": {
                "_id": 0,
                "code": "$clinic_history.code",
                "diagnostic": "$clinic_history.diagnostic",
                "doctor": "$clinic_history.doctor",
                "date": "$clinic_history.date",
                "status": "$clinic_history.status",
                "tooths": "$clinic_history.tooths"}},
            {'$lookup': {
                'from': "users",
                'localField': "doctor",
                'foreignField': "username",
                'as': "doctor_data"}},
            {'$unwind': "$doctor_data"},
            {"$project": {
                "code": 1,
                "date": 1,
                "diagnostic": 1,
                "tooths": 1,
                "status": 1,
                "doctor": 1,
                "doctor_name": "$doctor_data.name"}},
            {"$sort": {"code": 1}}
        ])

        diagnostic = list(cursor)
        if not diagnostic:
            return None
        return diagnostic

    def add_diagnostic(self, cpf, date, doctor, tooths, diagnostic, status=0):
        patient = self.find_patient(cpf)
        cursor = self.patients.aggregate([
            {'$match': {'cpf': cpf}},
            {'$unwind': '$clinic_history'},
            {'$group': {'_id': '', 'count': {'$sum': 1}}}
        ])
        result = list(cursor)
        if result:
            code = result[0]['count'] + 1
        else:
            code = 1
        document = {'code': code, 'date': date, 'doctor': doctor, 'tooths': tooths, 'diagnostic': diagnostic,
                    'status': status}
        if patient is None:
            return "Paciente não encontrado"
        try:
            self.patients.update_one({'cpf': cpf}, {'$push': {'clinic_history': document}})
        except errors.OperationFailure:
            return "Oops, Paciente não atualizado"
        return True

    def edit_diagnostic(self, cpf, code, status):
        patient = self.patients.find_one({'cpf': cpf, 'clinic_history.code': int(code)})
        if patient is None:
            return "Paciente não encontrado"
        try:
            self.patients.update_one({'cpf': cpf, 'clinic_history.code': int(code)},
                                     {'$set': {'clinic_history.$.status': status}})
        except errors.OperationFailure:
            return "Oops, Paciente não atualizado"
        return True

    def delete_diagnostic(self, cpf, code):
        patient = self.patients.find_one({'cpf': cpf})
        if patient is None:
            return "Paciente não encontrado"
        try:
            self.patients.update_one({'cpf': cpf}, {'$pull': {'clinic_history': {'code': int(code)}}})
        except errors.OperationFailure:
            return "Oops, Paciente não atualizado"
        return True

    def delete_patient(self, cpf):
        patient = self.find_patient(cpf)
        if patient is None:
            return "Paciente não encontrado"
        try:
            self.patients.update_one({'cpf': cpf,'status': 1}, {'$set': {'status': 0}})
        except errors.OperationFailure:
            return "Oops, Paciente não deletado"
        return True

    def list_patients(self, status=1):
        query = {'status': status}
        patients = self.patients.find(query)
        count = patients.count()
        if count > 0:
            return patients
        return None

    def get_patient_by_cpf(self, cpf, status=1):
        query = {'cpf': cpf, 'status': status}
        patient = self.patients.find_one(query)
        if patient is not None:
            return patient
        return None
