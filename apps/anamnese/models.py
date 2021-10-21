from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Patient:
    def __init__(self):
        self.db = database
        self.patients = self.db.patients


    def edit_patient(self, dni, name, date_of_birth, email, phone, address, visit_reason):
        patient = self.find_patient(dni)
        if patient is None:
            return "Paciente não encontrado"
        try:
            self.patients.update_one({'dni': dni}, {
                '$set': {'name': name, 'date_of_birth': date_of_birth, 'email': email, 'phone': phone,
                         'address': address, 'visit_reason': visit_reason}})
        except errors.OperationFailure:
            return "Oops, Paciente não atualizado"
        return True

    def edit_patient_notes(self, dni, notes):
        patient = self.find_patient(dni)
        if patient is None:
            return "Paciente não encontrado"
        try:
            self.patients.update_one({'dni': dni}, {'$set': {'notes': notes}})
        except errors.OperationFailure:
            return "Oops, Paciente não atualizado"
        return True

    def delete_patient(self, dni):
        patient = self.find_patient(dni)
        if patient is None:
            return "Paciente não encontrado"
        try:
            self.patients.update_one({'dni': dni}, {'$set': {'status': 0}})
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

    def get_patient_by_dni(self, dni, status=1):
        query = {'dni': dni, 'status': status}
        patient = self.patients.find_one(query)
        if patient is not None:
            return patient
        return None
