# inventario/urls.py
from django.urls import path
from . import views

app_name = "inventario"

urlpatterns = [
    path("", views.inventario_home, name="inventario"),
    path("stock/", views.stock_view, name="stock"),
    path("categorias/", views.category_list_create, name="categories"),
    path("productos/", views.product_list_create, name="products"),
    path("almacenes/", views.warehouse_list_create, name="warehouses"),
    path("movimientos/", views.movement_list_create, name="movements"),
]
