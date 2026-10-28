"""StockGuard - clasificacion del nivel de riesgo de inventario.

Practica autonoma de GitHub Actions. El caso es de ejemplo y no forma parte
del proyecto final RapidGo 360.
"""


def clasificar_stock(stock_actual: int, stock_minimo: int) -> str:
    """Clasifica el riesgo de inventario de un producto.

    Regla de negocio de la guia:

    - ``stock_actual == 0`` -> ``AGOTADO``
    - ``stock_actual <= stock_minimo * 0.5`` -> ``CRITICO``
    - ``stock_actual <= stock_minimo`` -> ``BAJO``
    - cualquier otro caso -> ``NORMAL``

    Un stock negativo o un stock minimo igual o menor que cero son invalidos.
    """
    if stock_actual < 0:
        raise ValueError("El stock actual no puede ser negativo")
    if stock_minimo <= 0:
        raise ValueError("El stock minimo debe ser mayor que cero")

    if stock_actual == 0:
        return "AGOTADO"
    if stock_actual <= stock_minimo * 0.5:
        return "CRITICO"
    if stock_actual <= stock_minimo:
        return "BAJO"
    return "NORMAL"
