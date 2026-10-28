"""StockGuard - clasificacion del nivel de riesgo de inventario.

Practica autonoma de GitHub Actions. El caso es de ejemplo y no forma parte
del proyecto final RapidGo 360.
"""

# Un producto se considera en sobrestock cuando supera este multiplo del minimo.
FACTOR_SOBRESTOCK = 2.0


def _validar_entradas(stock_actual: int, stock_minimo: int) -> None:
    """Valida las entradas comunes a todas las reglas de stock."""
    if stock_actual < 0:
        raise ValueError("El stock actual no puede ser negativo")
    if stock_minimo <= 0:
        raise ValueError("El stock minimo debe ser mayor que cero")


def clasificar_stock(stock_actual: int, stock_minimo: int) -> str:
    """Clasifica el riesgo de inventario de un producto.

    Regla de negocio de la guia:

    - ``stock_actual == 0`` -> ``AGOTADO``
    - ``stock_actual <= stock_minimo * 0.5`` -> ``CRITICO``
    - ``stock_actual <= stock_minimo`` -> ``BAJO``
    - cualquier otro caso -> ``NORMAL``

    Un stock negativo o un stock minimo igual o menor que cero son invalidos.
    """
    _validar_entradas(stock_actual, stock_minimo)

    if stock_actual == 0:
        return "AGOTADO"
    if stock_actual <= stock_minimo * 0.5:
        return "CRITICO"
    if stock_actual <= stock_minimo:
        return "BAJO"
    return "NORMAL"


def detectar_sobrestock(
    stock_actual: int,
    stock_minimo: int,
    factor: float = FACTOR_SOBRESTOCK,
) -> bool:
    """Indica si el inventario esta muy por encima del minimo requerido.

    El sobrestock inmoviliza capital y ocupa espacio de almacenamiento, asi que
    conviene detectarlo antes de reponer. Se considera sobrestock cuando
    ``stock_actual > stock_minimo * factor``.

    El limite es estricto: con ``stock_minimo=20`` y ``factor=2.0``, un stock de
    40 esta justo en el limite y **no** es sobrestock; 41 si lo es.

    Un stock negativo o un stock minimo igual o menor que cero son invalidos, y
    un factor menor o igual que 1 no describe sobrestock: seria clasificar como
    exceso algo que la regla de negocio considera normal o bajo.
    """
    _validar_entradas(stock_actual, stock_minimo)
    if factor <= 1:
        raise ValueError("El factor de sobrestock debe ser mayor que uno")

    return stock_actual > stock_minimo * factor
