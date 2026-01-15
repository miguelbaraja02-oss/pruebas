from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import redirect, render

from accounts.decorators import permission_required

from .forms import CategoryForm, InventoryMovementForm, ProductForm, WarehouseForm
from .models import Category, InventoryMovement, Product, Warehouse


@login_required
@permission_required(["inventario_access"])
def inventario_home(request):
    stats = {
        "categories": Category.objects.count(),
        "products": Product.objects.count(),
        "warehouses": Warehouse.objects.count(),
        "movements": InventoryMovement.objects.count(),
    }

    recent_movements = (
        InventoryMovement.objects.select_related("product", "warehouse")
        .order_by("-movement_date")[:8]
    )

    return render(
        request,
        "inventario/home.html",
        {
            "stats": stats,
            "recent_movements": recent_movements,
        },
    )


@login_required
@permission_required(["inventario_access"])
def stock_view(request):
    confirmed = InventoryMovement.objects.filter(status="CONFIRMED")

    decimal_zero = Value(0, output_field=DecimalField(max_digits=12, decimal_places=2))

    stock_rows = (
        confirmed.values(
            "product_id",
            "product__sku",
            "product__name",
            "product__unit_of_measure",
            "warehouse_id",
            "warehouse__code",
            "warehouse__name",
        )
        .annotate(
            entries=Coalesce(
                Sum("quantity", filter=Q(movement_type__in=["IN", "ADJ"])),
                decimal_zero,
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
            exits=Coalesce(
                Sum("quantity", filter=Q(movement_type="OUT")),
                decimal_zero,
                output_field=DecimalField(max_digits=12, decimal_places=2),
            ),
        )
        .annotate(
            balance=F("entries") - F("exits"),
        )
        .order_by("product__name", "warehouse__name")
    )

    stock_rows = list(stock_rows)
    for row in stock_rows:
        row["entries"] = row.get("entries") or 0
        row["exits"] = row.get("exits") or 0
        row["balance"] = row.get("balance") or 0

    return render(
        request,
        "inventario/stock.html",
        {
            "stock_rows": stock_rows,
        },
    )


# CRUD sencillos con formulario + listado en la misma vista


@login_required
@permission_required(["inventario_access"])
def category_list_create(request):
    categories = Category.objects.select_related("parent").order_by("name")
    form = CategoryForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        category = form.save(commit=False)
        if category.created_by_id is None:
            category.created_by = request.user
        category.save()
        messages.success(request, "Categoría guardada correctamente.")
        return redirect("inventario:categories")

    return render(
        request,
        "inventario/categories.html",
        {"form": form, "categories": categories},
    )


@login_required
@permission_required(["inventario_access"])
def product_list_create(request):
    products = (
        Product.objects.select_related("category")
        .order_by("name")
    )
    form = ProductForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        product = form.save(commit=False)
        if product.created_by_id is None:
            product.created_by = request.user
        product.save()
        messages.success(request, "Producto guardado correctamente.")
        return redirect("inventario:products")

    return render(
        request,
        "inventario/products.html",
        {"form": form, "products": products},
    )


@login_required
@permission_required(["inventario_access"])
def warehouse_list_create(request):
    warehouses = Warehouse.objects.select_related("manager").order_by("name")
    form = WarehouseForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        warehouse = form.save()
        messages.success(request, "Almacén guardado correctamente.")
        return redirect("inventario:warehouses")

    return render(
        request,
        "inventario/warehouses.html",
        {"form": form, "warehouses": warehouses},
    )


@login_required
@permission_required(["inventario_access"])
def movement_list_create(request):
    movements = (
        InventoryMovement.objects.select_related("product", "warehouse")
        .order_by("-movement_date")[:20]
    )
    form = InventoryMovementForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        movement = form.save(commit=False)
        if movement.performed_by_id is None:
            movement.performed_by = request.user
        movement.save()
        messages.success(request, "Movimiento registrado correctamente.")
        return redirect("inventario:movements")

    return render(
        request,
        "inventario/movements.html",
        {"form": form, "movements": movements},
    )


