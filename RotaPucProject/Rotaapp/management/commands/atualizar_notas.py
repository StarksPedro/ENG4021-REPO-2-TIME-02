from django.core.management.base import BaseCommand, CommandError

from Rotaapp.models import FonteNotasDeCorte
from Rotaapp.notas_corte import atualizar


class Command(BaseCommand):
    help = "Baixa o PDF da lista de CR da PUC-Rio e atualiza as notas de corte no banco."

    def add_arguments(self, parser):
        parser.add_argument("--url", help="usa (e passa a guardar) este endereço do PDF")
        parser.add_argument("--forcar", action="store_true",
                            help="lê e grava mesmo que o PDF seja igual ao da última vez")

    def handle(self, *args, **opcoes):
        fonte = FonteNotasDeCorte.obter()
        if opcoes["url"]:
            fonte.url = opcoes["url"]
            fonte.hash_pdf = ""
            fonte.save()
        try:
            mensagem = atualizar(fonte, forcar=opcoes["forcar"])
        except Exception as erro:
            raise CommandError(str(erro))
        self.stdout.write(self.style.SUCCESS(mensagem))