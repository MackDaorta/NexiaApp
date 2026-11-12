from django.db import models
from django.contrib.auth.models import User

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

class Curso(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    portada = models.ImageField(upload_to='cursos_portadas/', blank=True, null=True)
    categorias = models.ManyToManyField(Categoria, related_name='cursos')
    creador = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cursos_creados')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    precio = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    def __str__(self):
        return self.titulo

class Modulo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='modulos')
    titulo = models.CharField(max_length=200) # Ej: "Parte 1: Introducción"
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.curso.titulo} - {self.titulo}"

class Leccion(models.Model):
    modulo = models.ForeignKey(Modulo, on_delete=models.CASCADE, related_name='lecciones')
    titulo = models.CharField(max_length=200)
    orden = models.PositiveIntegerField(default=1)
    video = models.FileField(upload_to='lecciones_videos/', blank=True, null=True)
    pdf_adjunto = models.FileField(upload_to='lecciones_pdfs/', blank=True, null=True)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.modulo.titulo} -> {self.orden}. {self.titulo}"

class Inscripcion(models.Model):
    estudiante = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscripciones')
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='estudiantes_inscritos')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('estudiante', 'curso')

    def __str__(self):
        return f"{self.estudiante.username} inscrito en {self.curso.titulo}"