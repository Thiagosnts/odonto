from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Question:
    def __init__(self):
        self.db = database
        self.questions = self.db.questions


    def edit_question(self, dni, name, date_of_birth, email, phone, address, visit_reason):
        question = self.find_question(dni)
        if question is None:
            return "Paciente não encontrado"
        try:
            self.questions.update_one({'dni': dni}, {
                '$set': {'name': name, 'date_of_birth': date_of_birth, 'email': email, 'phone': phone,
                         'address': address, 'visit_reason': visit_reason}})
        except errors.OperationFailure:
            return "Oops, Paciente não atualizado"
        return True

    def edit_question_notes(self, dni, notes):
        question = self.find_question(dni)
        if question is None:
            return "Paciente não encontrado"
        try:
            self.questions.update_one({'dni': dni}, {'$set': {'notes': notes}})
        except errors.OperationFailure:
            return "Oops, Paciente não atualizado"
        return True

    def delete_question(self, dni):
        question = self.find_question(dni)
        if question is None:
            return "Paciente não encontrado"
        try:
            self.questions.update_one({'dni': dni}, {'$set': {'status': 0}})
        except errors.OperationFailure:
            return "Oops, Paciente não deletado"
        return True

    def list_questions(self, status=1):
        query = {'status': status}
        questions = self.questions.find(query)
        count = questions.count()
        if count > 0:
            return questions
        return None

    def get_question_by_dni(self, dni, status=1):
        query = {'dni': dni, 'status': status}
        question = self.questions.find_one(query)
        if question is not None:
            return question
        return None
