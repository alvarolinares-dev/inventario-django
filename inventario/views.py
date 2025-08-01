import openpyxl.workbook
import pandas as pd
import openpyxl
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone
from django.db.models import Sum

from .models import Producto, Entrada, Salida
from .forms import EntradaForm, SalidaForm

# Vista principal que muestra todos los productos con su total de entradas y salidas
def inicio(request):
    productos = Producto.objects.all()
    for producto in productos:
        producto.entradas = Entrada.objects.filter(producto=producto).aggregate(total=Sum('cantidad'))['total'] or 0
        producto.salidas = Salida.objects.filter(producto=producto).aggregate(total=Sum('cantidad'))['total'] or 0
    return render(request, 'inventario/inicio.html', {'productos': productos})

# Lista y permite editar los productos desde una vista
def lista_productos(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = get_object_or_404(Producto, id=producto_id)

        producto.nombre = request.POST.get('nombre')
        producto.codigo = request.POST.get('codigo')
        producto.proveedor = request.POST.get('proveedor')
        producto.precio_unitario = request.POST.get('precio')
        producto.peso_unitario = request.POST.get('peso_unitario')  # <- AÑADIR
        producto.unidad_medida = request.POST.get('unidad_medida')  # <- AÑADIR

        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']

        producto.save()
        return redirect('lista_productos')

    productos = Producto.objects.all()
    return render(request, 'inventario/productos.html', {'productos': productos})

# Registra una nueva entrada de producto
def registrar_entrada(request):
    if request.method == 'POST':
        nombre_producto = request.POST.get('producto_nombre')
        cantidad = int(request.POST.get('cantidad'))

        try:
            producto = Producto.objects.get(nombre=nombre_producto)
            Entrada.objects.create(producto=producto, cantidad=cantidad)
        except Producto.DoesNotExist:
            messages.error(request, 'Producto no encontrado')

        return redirect('entradas_view')

    productos = list(Producto.objects.values('nombre', 'codigo', 'proveedor'))
    entradas = Entrada.objects.all().order_by('-fecha')
    return render(request, 'inventario/entradas.html', {
        'productos': productos,
        'entradas': entradas,
        'productos_json': json.dumps(productos, cls=DjangoJSONEncoder)
    })

# Registra una nueva salida de producto
def registrar_salida(request):
    if request.method == 'POST':
        producto_nombre = request.POST.get("producto_nombre", "").strip()
        cantidad = request.POST.get("cantidad")

        try:
            cantidad = int(cantidad)
            if cantidad <= 0:
                raise ValueError("Cantidad inválida")
        except:
            messages.error(request, "Cantidad inválida. Debe ser un número positivo.")
            return redirect('salidas_view')

        try:
            producto = Producto.objects.get(nombre=producto_nombre)
        except Producto.DoesNotExist:
            messages.error(request, f"Producto '{producto_nombre}' no encontrado.")
            return redirect('salidas_view')

        Salida.objects.create(producto=producto, cantidad=cantidad)
        messages.success(request, "Salida registrada exitosamente.")
        return redirect('salidas_view')

    return redirect('salidas_view')

# Importa productos desde un archivo Excel
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

    return redirect('inicio')

# Devuelve información JSON de un producto específico
def producto_json(request, id):
    producto = get_object_or_404(Producto, id=id)
    data = {
        'id': producto.id,
        'nombre': producto.nombre,
        'codigo': producto.codigo,
        'proveedor': producto.proveedor,
        'precio_unitario': str(producto.precio_unitario) if producto.precio_unitario else 0,
        'peso_unitario': str(producto.peso_unitario) if producto.peso_unitario else '',
        'unidad_medida': producto.unidad_medida,
    }
    return JsonResponse(data)



# Edita los datos de un producto
def editar_productos(request):
    if request.method == 'POST':
        producto_id = request.POST.get('producto_id')
        producto = get_object_or_404(Producto, pk=producto_id)

        producto.nombre = request.POST.get('nombre')
        producto.codigo = request.POST.get('codigo')
        producto.proveedor = request.POST.get('proveedor')
        producto.precio_unitario = request.POST.get('precio_unitario')
        producto.peso_unitario = request.POST.get('peso_unitario')
        producto.unidad_medida = request.POST.get('unidad_medida')


        if 'imagen' in request.FILES:
            producto.imagen = request.FILES['imagen']

        producto.save()
        return redirect('inicio')

# Crea un nuevo producto desde el formulario
def crear_producto(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        codigo = request.POST.get('codigo')
        proveedor = request.POST.get('proveedor')
        tipo_adquisicion = request.POST.get('tipo_adquisicion')
        precio_unitario = request.POST.get('precio_unitario')
        imagen = request.FILES.get('imagen')
        peso_unitario = request.POST.get('peso_unitario')
        unidad_medida = request.POST.get('unidad_medida')


        nuevo_producto = Producto(
            nombre=nombre,
            codigo=codigo,
            proveedor=proveedor,
            tipo_adquisicion=tipo_adquisicion,
            precio_unitario=precio_unitario,
            peso_unitario=peso_unitario,
            unidad_medida=unidad_medida,
            imagen=imagen
            )

        nuevo_producto.save()
        return redirect('inicio')
    return redirect('inicio')

# Elimina un producto
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, id=id)
    if request.method == 'POST':
        producto.delete()
        return redirect('inicio')

# Importa entradas desde un archivo Excel
def importar_entradas(request):
    if request.method == 'POST':
        archivo = request.FILES['archivo_excel']
        workbook = openpyxl.load_workbook(archivo)
        hoja = workbook.active

        for fila in hoja.iter_rows(min_row=2, values_only=True):
            codigo, cantidad = fila[:2]

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

# Importa salidas desde un archivo Excel
def importar_salidas(request):
    if request.method == 'POST' and request.FILES.get('archivo_excel'):
        archivo = request.FILES['archivo_excel']
        try:
            df = pd.read_excel(archivo)

            for index, row in df.iterrows():
                codigo = str(row.get('codigo')).strip()
                cantidad = int(row.get('cantidad'))

                try:
                    producto = Producto.objects.get(codigo=codigo)
                    Salida.objects.create(producto=producto, cantidad=cantidad)
                except Producto.DoesNotExist:
                    messages.warning(request, f"Producto con código '{codigo}' no encontrado. Fila {index+2}")

            messages.success(request, "Importación completada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al procesar archivo: {str(e)}")

    return redirect('salidas_view')

# Vista que muestra todas las entradas
def entradas_view(request):
    productos = Producto.objects.all()
    entradas = Entrada.objects.select_related('producto').all().order_by('-fecha')
    productos_serializados = list(productos.values('nombre', 'codigo', 'proveedor'))

    return render(request, 'inventario/entradas.html', {
        'entradas': entradas,
        'productos': productos,
        'productos_json': json.dumps(productos_serializados, cls=DjangoJSONEncoder)
    })

# Vista que muestra todas las salidas
def salidas_view(request):
    productos = Producto.objects.all()
    salidas = Salida.objects.all().order_by('-fecha')
    productos_json = json.dumps(list(productos.values("nombre", "codigo", "proveedor")), cls=DjangoJSONEncoder)

    return render(request, 'inventario/salidas.html', {
        'salidas': salidas,
        'productos': productos,
        'productos_json': productos_json
    })

# Actualiza cantidad de una entrada existente (desde AJAX)
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

# Actualiza el producto asignado a una entrada (AJAX)
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

# Elimina una entrada existente (AJAX)
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

# Actualiza cantidad de salida
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

# Actualiza producto de una salida
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

# Elimina una salida existente
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

def pedidos_view(request):
    return render(request, 'inventario/pedidos.html')