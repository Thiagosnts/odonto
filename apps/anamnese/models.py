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

    def delete_anamnese(self, cpf):
        if self.find_anamnese(cpf) is None:
            return "Pergunta não encontrado"
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
            return True
        return False
