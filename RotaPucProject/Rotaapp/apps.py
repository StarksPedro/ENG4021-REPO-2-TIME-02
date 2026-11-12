from django.apps import AppConfig


class RotaappConfig(AppConfig):
    # Tipo do campo "id" criado automaticamente em cada modelo.
    # Fica escrito aqui para todos do grupo gerarem as mesmas migrações,
    # qualquer que seja a versão do Django instalada no computador
    # (o padrão mudou entre as versões e isso criava migrações trocando o id de todas as tabelas).
    default_auto_field = 'django.db.models.AutoField'
    name = 'Rotaapp'
