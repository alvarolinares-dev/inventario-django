from django import forms 
from .models import Producto, Entrada, Salida

# Formulario para registrar una nueva entrada de producto
class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        fields = ['producto', 'cantidad']  # Campos visibles en el formulario


# Formulario para registrar una salida, con validación de stock
class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        fields = ['producto', 'cantidad']  # Campos visibles en el formulario

    # Validación personalizada del formulario
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')

        # Validar si hay stock suficiente antes de guardar
        if producto and cantidad:
            entradas = producto.entrada_set.aggregate(total=forms.models.Sum('cantidad'))['total'] or 0
            salidas = producto.salida_set.aggregate(total=forms.models.Sum('cantidad'))['total'] or 0
            stock_actual = entradas - salidas
            
            if cantidad > stock_actual:
                raise forms.ValidationError(
                    f"No hay suficiente stock disponible. Stock actual: {stock_actual}"
                )

# Formulario para productos
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            'nombre',
            'proveedor',
            'tipo_adquisicion',
            'precio_unitario',
            'peso_unitario',
            'unidad_medida',
            'imagen',
        ]