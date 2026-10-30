from django.contrib import admin
from .models import (
    Pais, Curso, Universidade, ItemUniversidade, Depoimento, Programa, Aluno, Pergunta, Resposta,
    NotaDeCorte, PreRequisito, EtapaProcesso, BlocoEtapa, ContatoCoordenacao, PaginaInstitucional,
)

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


class ItemUniversidadeInline(admin.TabularInline):
    # Requisitos, certificados, custos, bolsas e documentos direto na página da universidade
    model = ItemUniversidade
    extra = 0


class DepoimentoInline(admin.StackedInline):
    model = Depoimento
    extra = 0


@admin.register(Universidade)
class UniversidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla", "pais", "cidade", "ranking", "numero_de_vagas_disponiveis")
    list_filter = ("pais", "pais__continente")
    search_fields = ("nome", "sigla")
    filter_horizontal = ("cursos",)
    inlines = [ProgramaInline, ItemUniversidadeInline, DepoimentoInline]


@admin.register(Depoimento)
class DepoimentoAdmin(admin.ModelAdmin):
    # A coordenação aprova os depoimentos por aqui
    list_display = ("autor", "universidade", "data", "aprovado")
    list_filter = ("aprovado", "universidade")
    list_editable = ("aprovado",)


@admin.register(Programa)
class ProgramaAdmin(admin.ModelAdmin):
    list_display = ("universidade", "tipo_de_intercambio", "nivel", "duracao", "prazo_de_inscricao")
    list_filter = ("tipo_de_intercambio", "nivel")


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ("nome", "email", "curso")
    search_fields = ("nome", "email")


class RespostaInline(admin.StackedInline):
    model = Resposta
    extra = 0


@admin.register(Pergunta)
class PerguntaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "autor", "curtidas", "data_criacao")
    search_fields = ("titulo", "descricao", "autor")
    inlines = [RespostaInline]


@admin.register(NotaDeCorte)
class NotaDeCorteAdmin(admin.ModelAdmin):
    list_display = ("departamento", "nota", "semestre")
    list_filter = ("semestre",)
    search_fields = ("departamento",)


@admin.register(PreRequisito)
class PreRequisitoAdmin(admin.ModelAdmin):
    list_display = ("texto", "ordem")
    list_editable = ("ordem",)


class BlocoEtapaInline(admin.StackedInline):
    # Os blocos (parágrafos, listas, tabelas...) são editados dentro do próprio passo
    model = BlocoEtapa
    extra = 0


@admin.register(EtapaProcesso)
class EtapaProcessoAdmin(admin.ModelAdmin):
    list_display = ("numero", "titulo")
    inlines = [BlocoEtapaInline]


@admin.register(ContatoCoordenacao)
class ContatoCoordenacaoAdmin(admin.ModelAdmin):
    list_display = ("__str__", "instagram")


@admin.register(PaginaInstitucional)
class PaginaInstitucionalAdmin(admin.ModelAdmin):
    list_display = ("titulo", "slug")
    prepopulated_fields = {"slug": ("titulo",)}
