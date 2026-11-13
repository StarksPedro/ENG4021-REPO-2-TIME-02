from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Pergunta, Resposta


class PerguntaForm(forms.ModelForm):
    # ModelForm: o Django monta o formulário a partir dos campos do modelo
    # e, no form.save(), já cria a Pergunta no banco de dados.
    class Meta:
        model = Pergunta
        fields = ["titulo", "descricao", "marcadores"]
        labels = {
            "titulo": "Título da Pergunta",
            "descricao": "Descrição detalhada",
            "marcadores": "Marcadores",
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
            # Como "marcadores" é ManyToMany, o Django criaria uma lista de seleção múltipla
            # (que exige segurar Ctrl). Com CheckboxSelectMultiple vira uma caixinha por marcador.
            # As opções saem da tabela Marcador, ou seja, do banco.
            "marcadores": forms.CheckboxSelectMultiple,
        }


class RespostaForm(forms.ModelForm):
    # Só o texto vem do formulário: a pergunta vem da URL e o autor vem de quem está logado
    # (os dois são preenchidos na view, com form.save(commit=False)).
    class Meta:
        model = Resposta
        fields = ["texto"]
        labels = {"texto": "Responder"}
        widgets = {
            # Mesmo id e placeholder do HTML original, para o CSS da página continuar funcionando
            "texto": forms.Textarea(attrs={
                "id": "resposta-principal",
                "rows": 4,
                "placeholder": "Compartilhe sua experiência ou resposta",
            }),
        }


class CadastroForm(UserCreationForm):
    # UserCreationForm já traz o nome de usuário e os dois campos de senha, com as validações
    # do Django (senha parecida com o nome, senha só com números, senhas diferentes...).
    # Aqui acrescentamos o nome e o e-mail.
    first_name = forms.CharField(label="Nome", max_length=150)
    email = forms.EmailField(label="E-mail")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name", "username", "email")
        labels = {"username": "Nome de usuário"}

    def clean_email(self):
        # Não deixa criar duas contas com o mesmo e-mail
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Já existe uma conta com este e-mail.")
        return email
