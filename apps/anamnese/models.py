from pymongo import cursor
from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Question:
    def __init__(self):
        self.db = database
        self.questions = self.db.questions


    def add_question(self, question_date):
        count = self.questions.find({}).count()
        code = count + 1

        question = {'code': code, 'question': question_date}
        try:
            self.questions.insert_one(question)
        except errors.OperationFailure:
            return "oops, mongo error"
        return True

    # def edit_question_notes(self, dni, notes):
    #     question = self.find_question(dni)
    #     if question is None:
    #         return "Paciente não encontrado"
    #     try:
    #         self.questions.update_one({'dni': dni}, {'$set': {'notes': notes}})
    #     except errors.OperationFailure:
    #         return "Oops, Paciente não atualizado"
    #     return True

    # def delete_question(self, dni):
    #     question = self.find_question(dni)
    #     if question is None:
    #         return "Paciente não encontrado"
    #     try:
    #         self.questions.update_one({'dni': dni}, {'$set': {'status': 0}})
    #     except errors.OperationFailure:
    #         return "Oops, Paciente não deletado"
    #     return True

    def list_questions(self):
    # def list_questions(self, status=1):
        # query = {'status': status}
        # questions = self.questions.find(query)
        cursor = self.questions.aggregate([])
        questions = list(cursor)

        count = len(questions)
        if count > 0:
            return questions
        return None

    # def get_question_by_dni(self, dni, status=1):
    #     query = {'dni': dni, 'status': status}
    #     question = self.questions.find_one(query)
    #     if question is not None:
    #         return question
    #     return None
