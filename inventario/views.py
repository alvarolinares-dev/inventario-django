import pandas as pd
import openpyxl
from django.shortcuts import render, redirect, get_object_or_404
from .models import Producto, Entrada, Salida
from django.db.models import Sum
from .forms import EntradaForm, SalidaForm
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.utils import timezone

# Create your views here.
def inicio(request):
    productos = Producto.objects.all()
    for producto in productos:
        producto.entradas = Entrada.objects.filter(producto=producto).aggregate(total= Sum('cantidad'))['total'] or 0
        producto.salidas = Salida.objects.filter(producto=producto).aggregate(total= Sum('cantidad'))['total'] or 0
    return render(request, 'inventario/inicio.html', {'productos': productos})

def lista_productos(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = get_object_or_404(Producto, id=producto_id)
        producto.nombre = request.POST.get('nombre')
        producto.codigo = request.POST.get('codigo')
        producto.proveedor = request.POST.get('proveedor')
        producto.precio_unitario = request.POST.get('precio')
        
        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
        
        producto.save()
        return redirect('lista_productos')
     
    productos = Producto.objects.all()
    return render(request, 'inventario/productos.html', {'productos': productos})

def registrar_entrada(request):
    if request.method == 'POST':
        nombre_producto = request.POST.get('producto_nombre')
        cantidad = int(request.POST.get('cantidad'))

        try:
            producto = Producto.objects.get(nombre=nombre_producto)
            Entrada.objects.create(producto=producto, cantidad=cantidad)
        except Producto.DoesNotExist:
            
            pass

        return redirect('registrar_entrada')

    productos = list(Producto.objects.values('nombre', 'codigo', 'proveedor'))
    entradas = Entrada.objects.all().order_by('-fecha')
    return render(request, 'inventario/entradas.html', {
        'productos': productos,
        'entradas': entradas
    })


    

def registrar_salida(request):
    if request.method == 'POST':
        nombre_producto = request.POST.get('producto_nombre')
        cantidad = int(request.POST.get('cantidad'))

        try:
            producto = Producto.objects.get(nombre=nombre_producto)
            Salida.objects.create(producto=producto, cantidad=cantidad)
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado')

        return redirect('registrar_salida')
    
    productos = list(Producto.objects.values('nombre', 'codigo', 'proveedor'))
    salidas = Salida.objects.all().order_by('-fecha')
    return render(request, 'inventario/salidas.html', {
        'productos': productos,
        'salidas': salidas,
        'productos_json': json.dumps(productos, cls=DjangoJSONEncoder)
    })




def importar_productos(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        archivo = request.FILES['archivo_excel']
        df = pd.read_excel(archivo)

        importados = 0

        for index, row in df.iterrows():
            try:
                nombre = str(row.get('nombre', '')).strip()
                tipo = str(row.get('tipo_adquisicion', '')).strip().upper()
                proveedor = str(row.get('proveedor', '')).strip()
                precio = row.get('precio_unitario', 0) or 0

                if not nombre or tipo not in ['F1', 'M1']:
                    continue

                producto = Producto(
                    nombre=nombre,
                    tipo_adquisicion=tipo,
                    proveedor=proveedor if proveedor else '',
                    precio_unitario=precio if precio else 0
                )
                producto.save()
                importados += 1

            except Exception as e:
                print(f"Error en fila {index + 1}: {e}")
                continue

        messages.success(request, f"{importados} productos importados correctamente.")

    return redirect('inicio')  # Siempre redirige al inicio


    return render(request, 'inicio')

def producto_json(request, id):
    producto = get_object_or_404(Producto, id=id)
    data = {
        'id': producto.id,
        'nombre': producto.nombre,
        'codigo': producto.codigo,
        'proveedor': producto.proveedor,
        'precio_unitario': str(producto.precio_unitario) if producto.precio_unitario else 0,
    }
    return JsonResponse(data)


def editar_productos(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = get_object_or_404(Producto, pk=producto_id)
        
        producto.nombre = request.POST.get('nombre')
        producto.codigo = request.POST.get('codigo')
        producto.proveedor = request.POST.get('proveedor')
        producto.precio_unitario = request.POST.get('precio_unitario')

        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']
        
        producto.save()
        return redirect('inicio')

def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        codigo = request.POST.get('codigo')
        proveedor = request.POST.get('proveedor')
        tipo_adquisicion = request.POST.get('tipo_adquisicion')
        precio_unitario = request.POST.get('precio_unitario')
        imagen = request.FILES.get('imagen')
        

        nuevo_producto = Producto(
            nombre=nombre,
            codigo=codigo,
            proveedor=proveedor,
            tipo_adquisicion=tipo_adquisicion,
            precio_unitario=precio_unitario,
            imagen=imagen
        )
        nuevo_producto.save()
        return redirect('inicio')
    return redirect('inicio')


def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('inicio')
        

def importar_entradas(request):
    if request.method == 'POST':
        archivo = request.FILES['archivo_excel']
        workbook = openpyxl.load_workbook(archivo)
        hoja = workbook.active

        for fila in hoja.iter_rows(min_row=2, values_only=True):
            codigo, cantidad = fila[:2]  # asegúrate del orden

            try:
                producto = Producto.objects.get(codigo=codigo)
                Entrada.objects.create(producto=producto, cantidad=int(cantidad))
            except Producto.DoesNotExist:
                messages.error(request, f"Producto con código '{codigo}' no encontrado.")
                continue
            except Exception as e:
                messages.error(request, f"Error en fila con código '{codigo}': {str(e)}")
                continue

        messages.success(request, "Entradas importadas exitosamente.")
        return redirect('registrar_entrada')


def importar_salidas(request):
    if request.method == 'POST':
        archivo =  request.FILES.get('archivo_excel')
        if archivo:
            df = pd.read_excel(archivo)
            for _, row in df.iterrows():
                try:
                    producto = Producto.objects.get(codigo=row['codigo'])
                    Salida.objects.create(producto=producto, cantidad=int(row['cantidad']))
                except Producto.DoesNotExist:
                    continue
        return redirect('registrar_salida')


@csrf_exempt
def actualizar_cantidad(request):
    if request.method == "POST":
        entrada_id = request.POST.get('entrada_id')
        cantidad = request.POST.get('cantidad')

        try:
            entrada = Entrada.objects.get(id=entrada_id)
            entrada.cantidad = cantidad
            entrada.save()
            return JsonResponse({"success": True})
        except Entrada.DoesNotExist:
            return JsonResponse({"success": False, "error": "Entrada no encontrada"})

    return JsonResponse({"success": False, "error": "Método inválido"})


@csrf_exempt
def actualizar_producto_entrada(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entrada_id = data['entrada_id']
            nuevo_producto = data['nuevo_producto']

            entrada = Entrada.objects.get(id=entrada_id)
            producto = Producto.objects.get(nombre=nuevo_producto)

            entrada.producto = producto
            entrada.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})
        
@csrf_exempt
def eliminar_entrada(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            entrada_id = data['entrada_id']
            entrada = Entrada.objects.get(id=entrada_id)
            entrada.delete()
            return JsonResponse({'success': True})
        except Entrada.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Entrada no encontrada'})

    return JsonResponse({'success': False, 'message': 'Método no permitido'})


def entradas_view(request):
    productos = Producto.objects.all()
    entradas = Entrada.objects.select_related('producto').all()
    productos_serializados = list(productos.values('nombre', 'codigo', 'proveedor'))

    return render(request, 'inventario/entradas.html', {
    'entradas': entradas,
    'productos': productos,
    'productos_json': json.dumps(productos_serializados, cls=DjangoJSONEncoder)
})


def salidas_view(request):
    productos = Producto.objects.all()
    salidas = Salida.objects.select_related('producto').order_by('-fecha')
    productos_json = [
        {
            'id': producto.id,
            'nombre': producto.nombre,
            'codigo': producto.codigo,
            'proveedor': producto.proveedor
        }
        for producto in productos
    ]
    return render(request, 'salidas.html', {
        'productos': productos,
        'salidas': salidas,
        'productos_json': productos_json
    })


def registrar_salida(request):
    if request.method == 'POST':
        nombre_producto = request.POST.get('producto_nombre')
        cantidad = request.POST.get('cantidad')

        try:
            producto = Producto.objects.get(nombre=nombre_producto)
            Salida.objects.create(
                producto=producto,
                cantidad=cantidad,
                fecha=timezone.now()
            )
            return redirect('registrar_salida')
        except Producto.DoesNotExist:
            return JsonResponse({'error': 'Producto no encontrado'}, status=400)

    return redirect('registrar_salida')


@csrf_exempt
def actualizar_cantidad_salida(request):
    if request.method == 'POST':
        salida_id = request.POST.get('salida_id')
        nueva_cantidad = request.POST.get('cantidad')

        try:
            salida = Salida.objects.get(id=salida_id)
            salida.cantidad = nueva_cantidad
            salida.save()
            return JsonResponse({'success': True})
        except Salida.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Salida no encontrada'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})


@csrf_exempt
def actualizar_producto_salida(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        salida_id = data.get('salida_id')
        nuevo_nombre = data.get('nuevo_producto')

        try:
            producto = Producto.objects.get(nombre=nuevo_nombre)
            salida = Salida.objects.get(id=salida_id)
            salida.producto = producto
            salida.save()
            return JsonResponse({'status': 'ok'})
        except (Producto.DoesNotExist, Salida.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Error al actualizar'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido'})


@csrf_exempt
def eliminar_salida(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        salida_id = data.get('salida_id')

        try:
            salida = Salida.objects.get(id=salida_id)
            salida.delete()
            return JsonResponse({'success': True})
        except Salida.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Salida no encontrada'})
    return JsonResponse({'success': False, 'message': 'Método no permitido'})
