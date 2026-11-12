from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from .models import Curso, Categoria, Modulo, Leccion, Inscripcion

# --- VALIDACIÓN DE ROLES (DEBEN IR PRIMERO) ---

def es_admin_o_soporte(user):
    return user.is_authenticated and (user.is_staff or user.groups.filter(name='Soporte').exists())

def es_admin(user):
    return user.is_authenticated and user.is_superuser


# --- VISTAS PÚBLICAS Y DE USUARIOS ---

def home(request):
    cursos_recientes = Curso.objects.all().order_by('-fecha_creacion')[:6]
    categorias = Categoria.objects.all()
    return render(request, 'cursos/home.html', {
        'cursos_recientes': cursos_recientes,
        'categorias': categorias
    })

def catalogo(request):
    categoria_slug = request.GET.get('categoria')
    cursos = Curso.objects.all()
    
    if categoria_slug:
        cursos = cursos.filter(categorias__slug=categoria_slug)
        
    categorias = Categoria.objects.all()
    return render(request, 'cursos/catalogo.html', {
        'cursos': cursos,
        'categorias': categorias,
        'categoria_activa': categoria_slug
    })

def nosotros(request):
    return render(request, 'cursos/nosotros.html')

def carrito(request):
    return render(request, 'cursos/carrito.html')

def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'cursos/registro.html', {'form': form})


# --- PROCESO DE COMPRA, INSCRIPCIÓN Y CLASES ---

@login_required(login_url='login')
def inscribir_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if curso.precio == 0:
        Inscripcion.objects.get_or_create(estudiante=request.user, curso=curso)
        return redirect('mis_cursos')
    request.session['curso_checkout_id'] = curso.id
    return redirect('checkout_falso')

@login_required(login_url='login')
def checkout_falso(request):
    curso_id = request.session.get('curso_checkout_id')
    curso = get_object_or_404(Curso, id=curso_id) if curso_id else None
    
    if request.method == 'POST':
        if curso:
            Inscripcion.objects.get_or_create(estudiante=request.user, curso=curso)
            if 'curso_checkout_id' in request.session:
                del request.session['curso_checkout_id']
        return redirect('mis_cursos')
        
    return render(request, 'cursos/checkout_falso.html', {'curso': curso})

@login_required(login_url='login')
def mis_cursos(request):
    inscripciones = Inscripcion.objects.filter(estudiante=request.user)
    return render(request, 'cursos/mis_cursos.html', {'inscripciones': inscripciones})

@login_required(login_url='login')
def ver_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if not request.user.is_superuser and not request.user.is_staff and not Inscripcion.objects.filter(estudiante=request.user, curso=curso).exists():
        return redirect('catalogo')
    return render(request, 'cursos/ver_curso.html', {'curso': curso})


# --- GESTIÓN DE CURSOS, MÓDULOS Y LECCIONES (ADMIN Y SOPORTE) ---

@user_passes_test(es_admin_o_soporte, login_url='login')
def lista_cursos_gestion(request):
    if request.user.is_superuser or request.user.is_staff:
        cursos = Curso.objects.all()
    else:
        cursos = Curso.objects.filter(creador=request.user)
    return render(request, 'cursos/gestion/lista_cursos.html', {'cursos': cursos})

@user_passes_test(es_admin_o_soporte, login_url='login')
def crear_curso(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio', 0.00)
        portada = request.FILES.get('portada')
        categorias_ids = request.POST.getlist('categorias')
        
        curso = Curso.objects.create(
            titulo=titulo,
            descripcion=descripcion,
            precio=precio,
            portada=portada,
            creador=request.user
        )
        curso.categorias.set(categorias_ids)
        return redirect('lista_cursos_gestion')
    
    categorias = Categoria.objects.all()
    return render(request, 'cursos/gestion/crear_curso.html', {'categorias': categorias})

@user_passes_test(es_admin_o_soporte, login_url='login')
def crear_modulo(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        orden = request.POST.get('orden', 1)
        Modulo.objects.create(curso=curso, titulo=titulo, orden=orden)
        return redirect('lista_cursos_gestion')
    return render(request, 'cursos/gestion/crear_modulo.html', {'curso': curso})

@user_passes_test(es_admin_o_soporte, login_url='login')
def crear_leccion(request, modulo_id):
    modulo = get_object_or_404(Modulo, id=modulo_id)
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        orden = request.POST.get('orden', 1)
        video = request.FILES.get('video')
        pdf_adjunto = request.FILES.get('pdf_adjunto')
        
        Leccion.objects.create(
            modulo=modulo,
            titulo=titulo,
            orden=orden,
            video=video,
            pdf_adjunto=pdf_adjunto
        )
        return redirect('lista_cursos_gestion')
    return render(request, 'cursos/gestion/crear_leccion.html', {'modulo': modulo})


# --- GESTIÓN DE USUARIOS Y SOPORTE (SOLO ADMIN) ---

@user_passes_test(es_admin, login_url='login')
def lista_usuarios(request):
    usuarios = User.objects.all()
    return render(request, 'cursos/gestion/lista_usuarios.html', {'usuarios': usuarios})

@user_passes_test(es_admin, login_url='login')
def crear_cuenta_soporte(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if username and password:
            user = User.objects.create_user(username=username, email=email, password=password)
            grupo_soporte, creado = Group.objects.get_or_create(name='Soporte')
            user.groups.add(grupo_soporte)
            user.is_staff = True
            user.save()
            return redirect('lista_usuarios')
            
    return render(request, 'cursos/gestion/crear_soporte.html')