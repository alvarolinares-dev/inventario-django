from django.db import models
from django.db.models import Sum

# Modelo principal: representa cada producto registrado en el sistema
class Producto(models.Model):
    # Opciones del tipo de adquisición: Fabricación o Compra/Venta
    TIPO_ADQUISICION_CHOICES = [
        ('F1', 'Fabricación'),
        ('M1', 'Compra/Venta'),
    ]

    # Campos del modelo Producto
    codigo = models.CharField(max_length=20, unique=True)  # Código único generado automáticamente
    nombre = models.CharField(max_length=100)  # Nombre del producto
    cantidad_inicial = models.PositiveIntegerField(default=0)  # Cantidad con la que inicia el stock
    imagen = models.ImageField(upload_to='productos/', blank=True, null='True')  # Imagen opcional del producto
    proveedor = models.CharField(max_length=200, blank=True, null=True)  # Nombre del proveedor (opcional)
    precio_unitario = models.PositiveIntegerField(default=0)  # Precio por unidad
    tipo_adquisicion = models.CharField(
        max_length=2,
        choices=TIPO_ADQUISICION_CHOICES,
        default='M1'
    )  # Tipo de adquisición (fabricado o comprado)

    # Método personalizado para guardar el producto
    def save(self, *args, **kwargs):
        # Si no hay código, se genera automáticamente
        if not self.codigo:
            prefix = self.tipo_adquisicion  # 'F1' o 'M1'
            letras = self.nombre[:2].upper()  # Primeras dos letras del nombre
            count = Producto.objects.filter(tipo_adquisicion=self.tipo_adquisicion).count() + 1
            correlativo = str(count).zfill(3)  # Número con 3 dígitos, con ceros a la izquierda
            self.codigo = f"{prefix}{letras}{correlativo}"  # Ejemplo: M1LA001
        super().save(*args, **kwargs)

    # Propiedad para calcular el stock actual en tiempo real
    @property
    def stock_actual(self):
        entradas = self.entrada_set.aggregate(total=Sum('cantidad'))['total'] or 0
        salidas = self.salida_set.aggregate(total=Sum('cantidad'))['total'] or 0
        return self.cantidad_inicial + entradas - salidas

    # Cómo se muestra el producto en el admin o en otros contextos
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# Modelo Entrada: representa el ingreso de productos al inventario
class Entrada(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Relación con Producto
    cantidad = models.PositiveBigIntegerField()  # Cantidad de unidades ingresadas
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha en que se registró la entrada

    # Representación del objeto Entrada
    def __str__(self):
        return f"{self.producto.nombre} +{self.cantidad} unidades"


# Modelo Salida: representa el retiro de productos del inventario
class Salida(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)  # Relación con Producto
    cantidad = models.PositiveBigIntegerField()  # Cantidad de unidades retiradas
    fecha = models.DateTimeField(auto_now_add=True)  # Fecha en que se registró la salida

    # Al guardar, valida que haya suficiente stock
    def save(self, *args, **kwargs):
        if self.producto.stock_actual >= self.cantidad:
            super().save(*args, **kwargs)
        else:
            raise ValueError("Stock Insuficiente para realizar la salida")

    # Representación del objeto Salida
    def __str__(self):
        return f"{self.producto.nombre} -{self.cantidad} unidades"
