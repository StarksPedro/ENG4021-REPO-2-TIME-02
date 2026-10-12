from django.db import models

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


class Curso(models.Model):
    nome = models.CharField(max_length=100)

    def __str__(self):
        return self.nome


class Universidade(models.Model):
    nome = models.CharField(max_length=100)
    sigla = models.CharField(max_length=15)
    site_oficial = models.URLField()
    ranking = models.PositiveIntegerField()
    foto = models.URLField()
    endereco = models.CharField(max_length=150)
    numero_de_vagas_disponiveis = models.PositiveIntegerField()
    pais = models.ForeignKey(Pais, on_delete=models.CASCADE, related_name="universidades")
    cursos = models.ManyToManyField(Curso, related_name="universidades", blank=True)

    def __str__(self):
        return self.nome


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