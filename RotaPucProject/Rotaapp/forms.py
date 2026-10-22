from django import forms
from .models import Pergunta


class PerguntaForm(forms.ModelForm):
    # ModelForm: o Django monta o formulário a partir dos campos do modelo
    # e, no form.save(), já cria a Pergunta no banco de dados.
    class Meta:
        model = Pergunta
        fields = ["titulo", "descricao"]
        labels = {
            "titulo": "Título da Pergunta",
            "descricao": "Descrição detalhada",
        }
        # Os widgets mantêm os mesmos id e placeholder do HTML original,
        # para o CSS da página continuar funcionando.
        widgets = {
            "titulo": forms.TextInput(attrs={
                "id": "titulo",
                "placeholder": "Digite o título...",
            }),
            "descricao": forms.Textarea(attrs={
                "id": "descricao",
                "placeholder": "Digite o problema...",
            }),
        }
