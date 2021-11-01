from pymongo import cursor
from dentaladmin import utils

database = utils.database_connection
errors = utils.database_errors


class Anamnese:
    def __init__(self):
        self.db = database
        self.anamnese = self.db.anamnese

    def create_anamnese(self, lista):
        try:
            self.anamnese.insert_many(lista)
        except errors.OperationFailure:
            return "oops, mongo error"

    # def find_question(self, code, status=1):
    #     question = self.questions.find_one({'code': int(code), 'status': 1})
    #     if not question:
    #         return None
    #     return question

    # def add_question(self, question_date, status=1):
    #     count = self.questions.find({}).count()
    #     code = count + 10

    #     question = {'code': code, 'question': question_date, 'status': status}
    #     try:
    #         self.questions.insert_one(question)
    #     except errors.OperationFailure:
    #         return "oops, mongo error"
    #     return True

    def delete_anamnese(self, cpf):
        # question = self.find_question(code)
        # if question is None:
        #     return "Pergunta não encontrado"
        try:
            x = self.anamnese.delete_many({"cpf":cpf})
        except errors.OperationFailure:
            return "Oops, Questão não deletada"
        return True

    def find_anamnese(self, cpf):
        query = {"cpf":cpf}
        cursor = self.anamnese.find(query)
        anamnese = cursor
        count = anamnese.count()

        if count > 0:
            return anamnese
        return None
