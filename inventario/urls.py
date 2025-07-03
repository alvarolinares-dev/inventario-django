from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('entradas/', views.registrar_entrada, name='registrar_entrada'),
    path('salidas/', views.registrar_salida, name= 'registrar_salida'),
    path('importar/', views.importar_productos, name='importar_productos'),
    path('productos/', views.lista_productos, name='lista_productos'),
    path('productos/<int:id>/json/', views.producto_json, name='producto_json'),
    path('editar_producto/', views.editar_productos, name= 'editar_producto'),
    path('crear_producto/', views.crear_producto, name='crear_producto'),
    path('producto/<int:id>/eliminar/', views.eliminar_producto, name='eliminar_producto'),
    path('entradas/', views.registrar_entrada, name='registrar_entrada'),
    path('entradas/importar/', views.importar_entradas, name='importar_entradas'),
    path('salidas/importar/', views.importar_salidas, name='importar_salidas'),
    path('entradas/actualizar_cantidad/', views.actualizar_cantidad, name='actualizar_cantidad'),
    path('entradas/actualizar-producto/', views.actualizar_producto_entrada, name='actualizar_producto_entrada'),
    path('entradas/eliminar/', views.eliminar_entrada_ajax, name='eliminar_entrada_ajax'),


]

