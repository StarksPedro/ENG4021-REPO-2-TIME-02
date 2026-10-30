from django.db import models
from django.utils.text import slugify

class Pais(models.Model):
    nome = models.CharField(max_length=70)
    continente = models.CharField(max_length=15)
    idioma_oficial = models.CharField(max_length=25)
    moeda = models.CharField(max_length=45)
    requisitos_para_entrar = models.TextField()

    class Meta:
        verbose_name = "País"
        verbose_name_plural = "Países"

    def __str__(self):
        return self.nome

    @property
    def imagem(self):
        # Caminho da foto do país dentro da pasta static (ex.: "css/Pedro/alemanha.jpg").
        # slugify tira acentos e espaços: "Itália" vira "italia".
        return f"css/Pedro/{slugify(self.nome)}.jpg"


class Curso(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Universidade(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=15)
    site_oficial = models.URLField()
    ranking = models.PositiveIntegerField()
    foto = models.URLField(blank=True)
    endereco = models.CharField(max_length=150)
    numero_de_vagas_disponiveis = models.PositiveIntegerField()
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name="universidades")
    cursos = models.ManyToManyField(Curso, related_name="universidades", blank=True)
    # Campos da página de detalhe da universidade. Têm default="" para a migração
    # funcionar nas universidades que já estavam cadastradas.
    cidade = models.CharField(max_length=60, blank=True, default="")
    sobre = models.TextField(blank=True, default="")
    perfil_academico = models.TextField(blank=True, default="")
    email_contato = models.EmailField(blank=True, default="")

    def __str__(self):
        return self.nome


class ItemUniversidade(models.Model):
    # Cada linha das listas da página da universidade (requisitos, certificados,
    # custos, bolsas e documentos) é um item, ligado à sua universidade.
    TIPOS = [
        ("requisito", "Requisito acadêmico"),
        ("certificado", "Certificado de idioma aceito"),
        ("custo", "Custo"),
        ("bolsa", "Bolsa"),
        ("documento", "Documento necessário"),
    ]
    universidade = models.ForeignKey(Universidade, on_delete=models.CASCADE, related_name="itens")
    tipo = models.CharField(max_length=20, choices=TIPOS)
    texto = models.CharField(max_length=200)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Item da universidade"
        verbose_name_plural = "Itens da universidade"
        ordering = ["universidade", "tipo", "ordem"]

    def __str__(self):
        return f"{self.get_tipo_display()}: {self.texto}"


class Depoimento(models.Model):
    # Relatos de ex-intercambistas. Só aparecem no site depois que a
    # coordenação marca "aprovado" pelo /admin.
    universidade = models.ForeignKey(Universidade, on_delete=models.CASCADE, related_name="depoimentos")
    autor = models.CharField(max_length=100)
    texto = models.TextField()
    data = models.DateField(auto_now_add=True)
    aprovado = models.BooleanField(default=False)

    def __str__(self):
        return f"Depoimento de {self.autor} sobre {self.universidade}"


class Programa(models.Model):
    universidade = models.ForeignKey(Universidade, on_delete=models.CASCADE, related_name="programas")
    nivel = models.CharField(max_length=30)
    custo = models.DecimalField(max_digits=10, decimal_places=2)
    duracao = models.PositiveIntegerField(help_text="em meses")
    prazo_de_inscricao = models.DateField()
    idioma = models.CharField(max_length=40)
    tipo_de_intercambio = models.CharField(max_length=20)
    numero_de_vagas = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.tipo_de_intercambio} em {self.universidade}"


class Aluno(models.Model):
    nome = models.CharField(max_length=800)
    email = models.EmailField(unique=True)
    senha = models.CharField(max_length=140)
    curso = models.ForeignKey(Curso, on_delete=models.PROTECT, related_name="alunos")
    universidades_procuradas = models.ManyToManyField(
        Universidade, blank=True, related_name="alunos_interessados"
    )

    def __str__(self):
        return self.nome


class Pergunta(models.Model):
    titulo = models.CharField(max_length=150)
    descricao = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    # Usados nos cards do fórum. Têm default para o formulário de "Nova pergunta"
    # continuar funcionando sem pedir esses campos.
    autor = models.CharField(max_length=100, blank=True, default="")
    curtidas = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Pergunta"
        verbose_name_plural = "Perguntas"

    def __str__(self):
        return self.titulo


class Resposta(models.Model):
    pergunta = models.ForeignKey(Pergunta, on_delete=models.CASCADE, related_name="respostas")
    autor = models.CharField(max_length=100)
    texto = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    curtidas = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["data_criacao"]

    def __str__(self):
        return f"Resposta de {self.autor} em {self.pergunta}"


class NotaDeCorte(models.Model):
    # Lista de CR do processo seletivo. O departamento é texto (e não ligado a Curso)
    # porque a lista tem 25 departamentos e o modelo Curso só tem os cursos das parceiras.
    departamento = models.CharField(max_length=60)
    nota = models.DecimalField(max_digits=4, decimal_places=2)
    semestre = models.CharField(max_length=10, help_text="ex.: 2026.2")

    class Meta:
        verbose_name = "Nota de corte"
        verbose_name_plural = "Notas de corte"
        ordering = ["departamento"]

    def __str__(self):
        return f"{self.departamento} ({self.semestre})"

    @property
    def nota_formatada(self):
        # 7.20 vira "7,2", igual à tabela original
        return f"{self.nota.normalize():f}".replace(".", ",")


class PreRequisito(models.Model):
    texto = models.CharField(max_length=200)
    ordem = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Pré-requisito"
        verbose_name_plural = "Pré-requisitos"
        ordering = ["ordem"]

    def __str__(self):
        return self.texto


class EtapaProcesso(models.Model):
    numero = models.PositiveIntegerField(unique=True)
    titulo = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Etapa do processo seletivo"
        verbose_name_plural = "Etapas do processo seletivo"
        ordering = ["numero"]

    def __str__(self):
        return f"Passo {self.numero} - {self.titulo}"


class BlocoEtapa(models.Model):
    # Cada passo tem partes de formatos diferentes (parágrafo, lista, tabela...).
    # Cada parte é um bloco; o "tipo" diz ao template como mostrar o texto.
    TIPOS = [
        ("paragrafo", "Parágrafo"),
        ("subtitulo", "Subtítulo"),
        ("lista_numerada", "Lista numerada (um item por linha)"),
        ("lista", "Lista com marcadores (um item por linha)"),
        ("chips", "Etiquetas (uma por linha)"),
        ("nota", "Nota"),
        ("destaque", "Destaque"),
        ("caixa", "Caixa (um parágrafo por linha)"),
        ("tabela", "Tabela (uma linha por linha, colunas separadas por |)"),
        ("cards", "Cards (um por linha: título | texto)"),
    ]
    etapa = models.ForeignKey(EtapaProcesso, on_delete=models.CASCADE, related_name="blocos")
    ordem = models.PositiveIntegerField(default=0)
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(
        max_length=150, blank=True, default="",
        help_text="Tabela: cabeçalho com colunas separadas por |. Caixa: título em negrito (opcional).",
    )
    texto = models.TextField()

    class Meta:
        verbose_name = "Bloco da etapa"
        verbose_name_plural = "Blocos da etapa"
        ordering = ["etapa", "ordem"]

    def __str__(self):
        return f"{self.etapa} - {self.get_tipo_display()}"

    @property
    def itens(self):
        # Listas, chips e caixas: cada linha do texto vira um item
        return [linha.strip() for linha in self.texto.splitlines() if linha.strip()]

    @property
    def colunas(self):
        # Tabelas e cards: "TOEFL IBT | 80" vira ["TOEFL IBT", "80"]
        return [[parte.strip() for parte in item.split("|")] for item in self.itens]

    @property
    def cabecalho(self):
        return [parte.strip() for parte in self.titulo.split("|")]


class ContatoCoordenacao(models.Model):
    # Um único registro com os dados da coordenação (CCCI). Campos com várias
    # linhas guardam um item por linha (ex.: um telefone por linha).
    endereco = models.TextField()
    emails = models.TextField()
    telefones = models.TextField()
    instagram = models.CharField(max_length=50)
    horario = models.TextField()

    class Meta:
        verbose_name = "Contato da coordenação"
        verbose_name_plural = "Contato da coordenação"

    def __str__(self):
        return "Contato da coordenação"


class PaginaInstitucional(models.Model):
    # Textos de páginas institucionais (ex.: "Quem somos"), editáveis pelo /admin
    slug = models.SlugField(unique=True)
    selo = models.CharField(max_length=40)
    titulo = models.CharField(max_length=100)
    texto = models.TextField(help_text="Separe os parágrafos com uma linha em branco.")

    class Meta:
        verbose_name = "Página institucional"
        verbose_name_plural = "Páginas institucionais"

    def __str__(self):
        return self.titulo
