"""Pruebas de las reglas de clasificacion y sobrestock."""

import pytest

from src.inventario import clasificar_stock, detectar_sobrestock


def test_stock_agotado():
    assert clasificar_stock(0, 20) == "AGOTADO"


def test_stock_critico():
    assert clasificar_stock(7, 20) == "CRITICO"


def test_stock_bajo():
    assert clasificar_stock(15, 20) == "BAJO"


def test_stock_normal():
    assert clasificar_stock(30, 20) == "NORMAL"


def test_stock_invalido():
    with pytest.raises(ValueError):
        clasificar_stock(-2, 20)


def test_sobrestock_con_stock_muy_alto():
    # 45 > 20 * 2.0 -> hay exceso.
    assert detectar_sobrestock(45, 20) is True


def test_sobrestock_en_el_limite_no_alerta():
    # 40 == 20 * 2.0 -> el limite es estricto, todavia no es sobrestock.
    assert detectar_sobrestock(40, 20) is False


def test_sobrestock_no_alerta_con_stock_normal():
    assert detectar_sobrestock(30, 20) is False


def test_sobrestock_rechaza_stock_negativo():
    with pytest.raises(ValueError):
        detectar_sobrestock(-1, 20)


def test_sobrestock_rechaza_factor_invalido():
    with pytest.raises(ValueError):
        detectar_sobrestock(100, 20, factor=1.0)
