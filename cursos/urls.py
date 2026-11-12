from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('nosotros/', views.nosotros, name='nosotros'),
    path('carrito/', views.carrito, name='carrito'),
    path('registro/', views.registro, name='registro'),
    
    # Proceso de Inscripción / Checkout Falso
    path('curso/<int:curso_id>/inscribir/', views.inscribir_curso, name='inscribir_curso'),
    path('checkout/', views.checkout_falso, name='checkout_falso'),
    path('mis-cursos/', views.mis_cursos, name='mis_cursos'),
    path('curso/<int:curso_id>/aprender/', views.ver_curso, name='ver_curso'),

    # Panel de Gestión (Admin y Soporte)
    path('gestion/cursos/', views.lista_cursos_gestion, name='lista_cursos_gestion'),
    path('gestion/cursos/crear/', views.crear_curso, name='crear_curso'),
    path('gestion/cursos/<int:curso_id>/modulo/crear/', views.crear_modulo, name='crear_modulo'),
    path('gestion/modulo/<int:modulo_id>/leccion/crear/', views.crear_leccion, name='crear_leccion'),
    
    # Gestión de Usuarios (Solo Admin)
    path('gestion/usuarios/', views.lista_usuarios, name='lista_usuarios'),
    path('gestion/usuarios/crear-soporte/', views.crear_cuenta_soporte, name='crear_cuenta_soporte'),
]