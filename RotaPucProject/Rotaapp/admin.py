from django.contrib import admin
from .models import Pais, Curso, Universidade, Programa, Aluno, Pergunta

# Registrando os modelos no admin para poder cadastrar, editar e apagar os dados
# pelo /admin. Os list_display escolhem as colunas que aparecem na listagem,
# search_fields cria a barra de busca e list_filter cria os filtros da lateral.


@admin.register(Pais)
class PaisAdmin(admin.ModelAdmin):
    list_display = ("nome", "continente", "idioma_oficial", "moeda")
    list_filter = ("continente",)
    search_fields = ("nome",)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    search_fields = ("nome",)


class ProgramaInline(admin.TabularInline):
    # Permite cadastrar os programas direto na página da universidade
    model = Programa
    extra = 0


@admin.register(Universidade)
class UniversidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla", "pais", "ranking", "numero_de_vagas_disponiveis")
    list_filter = ("pais", "pais__continente")
    search_fields = ("nome", "sigla")
    filter_horizontal = ("cursos",)
    inlines = [ProgramaInline]


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ("universidade", "tipo_de_intercambio", "nivel", "duracao", "prazo_de_inscricao")
    list_filter = ("tipo_de_intercambio", "nivel")


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "curso")
    search_fields = ("nome", "email")


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "data_criacao")
    search_fields = ("titulo", "descricao")
