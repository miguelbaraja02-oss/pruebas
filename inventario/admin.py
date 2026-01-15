from django.contrib import admin

from .models import Category, InventoryMovement, Product, Warehouse


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
	list_display = ("name", "parent", "is_active", "created_at")
	list_filter = ("is_active",)
	search_fields = ("name", "description")


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = (
		"sku",
		"name",
		"category",
		"product_type",
		"is_active",
		"unit_of_measure",
	)
	list_filter = ("product_type", "is_active", "category")
	search_fields = ("sku", "name", "description")


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
	list_display = ("code", "name", "city", "is_active", "manager")
	list_filter = ("is_active",)
	search_fields = ("code", "name", "city")


@admin.register(InventoryMovement)
class InventoryMovementAdmin(admin.ModelAdmin):
	list_display = (
		"product",
		"warehouse",
		"movement_type",
		"quantity",
		"movement_date",
		"status",
	)
	list_filter = ("movement_type", "status", "warehouse")
	search_fields = ("product__name", "reference_document", "reason")
	autocomplete_fields = ("product", "warehouse", "performed_by")
