from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    
    # Productos
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/<int:id>/json/', views.producto_json, name='producto_json'),
    path('crear_producto/', views.crear_producto, name='crear_producto'),
    path('editar_producto/', views.editar_productos, name='editar_producto'),
    path('producto/<int:id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('importar/', views.importar_productos, name='importar_productos'),

    # Entradas
    path('entradas/', views.entradas_view, name='registrar_entrada'),  # Página principal
    path('registrar_entrada/', views.registrar_entrada, name='registrar_entrada_post'),  # Para formulario POST
    path('entradas/importar/', views.importar_entradas, name='importar_entradas'),
    path('entradas/actualizar_cantidad/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('entradas/actualizar-producto/', views.actualizar_producto_entrada, name='actualizar_producto_entrada'),
    path('entradas/eliminar/', views.eliminar_entrada, name='eliminar_entrada'),

    # Salidas
    path('salidas/', views.registrar_salida, name= 'registrar_salida'),
    path('salidas/importar/', views.importar_salidas, name='importar_salidas'),
]
