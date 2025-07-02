from django.db import models
from django.db.models import Sum



# Create your models here.
class Producto(models.Model):
    TIPO_ADQUISICION_CHOICES = [
        ('F1', 'Fabricación'),
        ('M1', 'Compra/Venta'),
    ]
    
    
    
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    cantidad_inicial = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/', blank=True, null='True')
    proveedor = models.CharField(max_length=200, blank=True, null=True )
    precio_unitario= models.PositiveIntegerField(default=0) 
    tipo_adquisicion = models.CharField(max_length=2, choices=TIPO_ADQUISICION_CHOICES, default='M1')
    
    def save(self, *args, **kwargs):
        if not self.codigo:
            prefix = self.tipo_adquisicion
            letras = self.nombre[:2].upper()
            count = Producto.objects.filter(tipo_adquisicion=self.tipo_adquisicion).count() + 1
            correlativo = str(count).zfill(3)
            self.codigo = f"{prefix}{letras}{correlativo}"
        super().save(*args, **kwargs)


    @property
    def stock_actual(self):
        entradas = self.entrada_set.aggregate(total=Sum('cantidad'))['total'] or 0
        salidas = self.salida_set.aggregate(total=Sum('cantidad'))['total'] or 0
        return self.cantidad_inicial + entradas - salidas
    

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
class Entrada(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveBigIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.producto.nombre} +{self.cantidad} unidades"

    
class Salida(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveBigIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.producto.stock_actual >= self.cantidad:
            super().save(*args, **kwargs)
        else:
            raise ValueError("Stock Insuficiente para realizar la salida")
    
    def __str__(self):
        return f"{self.producto.nombre} -{self.cantidad} unidades"