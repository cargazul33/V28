from .nissei import buscar as buscar_nissei
from .cellshop import buscar as buscar_cellshop
from .shoppingchina import buscar as buscar_shoppingchina
from .tupi import buscar as buscar_tupi
from .visaovip import buscar as buscar_visaovip
from .mega import buscar as buscar_mega
from .atacado import buscar as buscar_atacado
from .mercadolibre import buscar as buscar_mercadolibre


PROVEEDORES_PARAGUAY = [
    buscar_nissei,
    buscar_cellshop,
    buscar_shoppingchina,
    buscar_tupi,
    buscar_visaovip,
    buscar_mega,
    buscar_atacado,
]

PROVEEDORES_ARGENTINA = [
    buscar_mercadolibre,
]


def buscar_en_paraguay(producto):
    resultados = []

    for proveedor in PROVEEDORES_PARAGUAY:
        try:
            r = proveedor(producto)
            if r:
                resultados.append(r)
        except Exception:
            continue

    return resultados


def buscar_en_argentina(producto):
    resultados = []

    for proveedor in PROVEEDORES_ARGENTINA:
        try:
            r = proveedor(producto)
            if r:
                resultados.append(r)
        except Exception:
            continue

    return resultados
