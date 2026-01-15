from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Category(models.Model):
	name = models.CharField(max_length=100, unique=True)
	description = models.TextField(blank=True)
	is_active = models.BooleanField(default=True)
	parent = models.ForeignKey(
		"self", null=True, blank=True, related_name="children", on_delete=models.SET_NULL
	)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="categories_created",
	)

	class Meta:
		verbose_name = "Categoría"
		verbose_name_plural = "Categorías"
		ordering = ["name"]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return self.name


class Product(models.Model):
	PRODUCT_TYPES = (
		("stock", "Almacenable"),
		("service", "Servicio"),
	)

	sku = models.CharField(max_length=50, unique=True)
	name = models.CharField(max_length=150)
	category = models.ForeignKey(
		Category, related_name="products", on_delete=models.PROTECT
	)
	product_type = models.CharField(
		max_length=20, choices=PRODUCT_TYPES, default="stock"
	)
	is_active = models.BooleanField(default=True)
	description = models.TextField(blank=True)
	unit_of_measure = models.CharField(max_length=30, default="unidad")
	purchase_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	sale_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	min_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	max_stock = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	allow_negative_stock = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)
	created_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="products_created",
	)

	class Meta:
		verbose_name = "Producto"
		verbose_name_plural = "Productos"
		ordering = ["name"]
		indexes = [
			models.Index(fields=["sku"]),
			models.Index(fields=["name"]),
		]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return f"{self.sku} - {self.name}"


class Warehouse(models.Model):
	name = models.CharField(max_length=120)
	code = models.CharField(max_length=30, unique=True)
	is_active = models.BooleanField(default=True)
	address = models.CharField(max_length=255, blank=True)
	city = models.CharField(max_length=80, blank=True)
	notes = models.TextField(blank=True)
	manager = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="warehouses_managed",
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Almacén"
		verbose_name_plural = "Almacenes"
		ordering = ["name"]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return f"{self.code} - {self.name}"


class InventoryMovement(models.Model):
	MOVEMENT_TYPES = (
		("IN", "Entrada"),
		("OUT", "Salida"),
		("ADJ", "Ajuste"),
		("TRF", "Transferencia"),
	)
	STATUS_CHOICES = (
		("CONFIRMED", "Confirmado"),
		("VOID", "Anulado"),
	)

	product = models.ForeignKey(
		Product, related_name="movements", on_delete=models.PROTECT
	)
	warehouse = models.ForeignKey(
		Warehouse, related_name="movements", on_delete=models.PROTECT
	)
	movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
	quantity = models.DecimalField(
		max_digits=12,
		decimal_places=2,
		validators=[MinValueValidator(0)],
	)
	movement_date = models.DateTimeField(default=timezone.now)
	reason = models.CharField(max_length=255, blank=True)
	reference_document = models.CharField(max_length=100, blank=True)
	performed_by = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		null=True,
		blank=True,
		on_delete=models.SET_NULL,
		related_name="inventory_movements_performed",
	)
	unit_cost = models.DecimalField(
		max_digits=12, decimal_places=2, null=True, blank=True
	)
	total_cost = models.DecimalField(
		max_digits=12, decimal_places=2, null=True, blank=True
	)
	status = models.CharField(
		max_length=12, choices=STATUS_CHOICES, default="CONFIRMED"
	)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		verbose_name = "Movimiento de Inventario"
		verbose_name_plural = "Movimientos de Inventario"
		ordering = ["-movement_date", "-id"]
		indexes = [
			models.Index(fields=["product", "warehouse", "movement_date"]),
		]

	def __str__(self) -> str:  # pragma: no cover - trivial
		return f"{self.get_movement_type_display()} {self.product} ({self.quantity})"

	def save(self, *args, **kwargs):
		# Ensure total_cost is derived when possible to keep records consistent.
		if self.unit_cost is not None and self.total_cost is None:
			self.total_cost = self.unit_cost * self.quantity
		super().save(*args, **kwargs)
