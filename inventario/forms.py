from django import forms

from .models import Category, InventoryMovement, Product, Warehouse


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description", "is_active", "parent"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "sku",
            "name",
            "category",
            "product_type",
            "is_active",
            "description",
            "unit_of_measure",
            "purchase_price",
            "sale_price",
            "min_stock",
            "max_stock",
            "allow_negative_stock",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class WarehouseForm(forms.ModelForm):
    class Meta:
        model = Warehouse
        fields = [
            "name",
            "code",
            "is_active",
            "address",
            "city",
            "notes",
            "manager",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }


class InventoryMovementForm(forms.ModelForm):
    class Meta:
        model = InventoryMovement
        fields = [
            "product",
            "warehouse",
            "movement_type",
            "quantity",
            "movement_date",
            "reason",
            "reference_document",
            "unit_cost",
            "total_cost",
            "status",
        ]
        widgets = {
            "movement_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "reason": forms.Textarea(attrs={"rows": 2}),
        }

    def clean(self):
        cleaned = super().clean()
        # Derive total_cost if missing and unit_cost is provided.
        unit_cost = cleaned.get("unit_cost")
        total_cost = cleaned.get("total_cost")
        qty = cleaned.get("quantity")
        if unit_cost is not None and total_cost is None and qty is not None:
            cleaned["total_cost"] = unit_cost * qty
        return cleaned
