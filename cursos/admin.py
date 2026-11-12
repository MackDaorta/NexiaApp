from django.contrib import admin
from .models import Categoria, Curso, Modulo, Leccion, Inscripcion

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}

class LeccionInline(admin.TabularInline):
    model = Leccion
    extra = 1

@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'curso', 'orden')
    inlines = [LeccionInline]

class ModuloInline(admin.TabularInline):
    model = Modulo
    extra = 1

@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'creador', 'precio', 'fecha_creacion')
    search_fields = ('titulo', 'descripcion')
    list_filter = ('categorias', 'creador')
    filter_horizontal = ('categorias',)
    inlines = [ModuloInline]

@admin.register(Inscripcion)
class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('estudiante', 'curso', 'fecha_inscripcion')
    list_filter = ('curso', 'fecha_inscripcion')