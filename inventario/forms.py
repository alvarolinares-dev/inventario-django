from django import forms
from .models import Entrada, Salida

class EntradaForm(forms.ModelForm):
    class Meta:
        model = Entrada
        fields = ['producto', 'cantidad']

class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        fields = ['producto', 'cantidad']
    
    def clean(self):
        cleaned_data = super().clean()
        producto = cleaned_data.get('producto')
        cantidad = cleaned_data.get('cantidad')

        if producto and cantidad:
            entradas= producto.entrada_set.aggregate(total=forms.models.Sum('cantidad'))['total'] or 0
            salidas = producto.salida_set.aggregate(total=forms.models.Sum('cantidad'))['total'] or 0
            stock_actual = entradas - salidas
            
            if cantidad > stock_actual:
                raise forms.ValidationError(f"No hay suficiente stock. Stock actual: {stock_actual}")
        
        

