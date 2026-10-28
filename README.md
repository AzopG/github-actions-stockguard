# StockGuard — Práctica de GitHub Actions

Repositorio de práctica de la guía **"Introducción práctica a GitHub Actions"**
(Línea de Profundización I — Big Data).

El caso **StockGuard** clasifica el riesgo de inventario de un producto de supermercado.
Es un ejemplo didáctico: **no** forma parte del proyecto final RapidGo 360.

## Regla de negocio

| Condición | Resultado |
| --- | --- |
| `stock_actual == 0` | `AGOTADO` |
| `stock_actual <= stock_minimo * 0.5` | `CRITICO` |
| `stock_actual <= stock_minimo` | `BAJO` |
| cualquier otro caso | `NORMAL` |
| `stock_actual < 0` o `stock_minimo <= 0` | `ValueError` |

Con `stock_minimo = 20` y `stock_actual = 7`: el 50 % del mínimo es 10, y 7 ≤ 10, así que
el resultado es **CRITICO**.

## Estructura

```
github-actions-stockguard/
|-- .github/
|   `-- workflows/
|       `-- ci.yml
|-- src/
|   |-- __init__.py
|   `-- inventario.py
|-- tests/
|   `-- test_inventario.py
|-- docs/
|   |-- analisis.md
|   `-- evidencias.md
|-- requirements.txt
`-- README.md
```

## Ejecutar en local

```bash
python -m pip install -r requirements.txt
pytest -v
```

`pytest` debe ejecutarse **desde la raíz del repositorio**: el import es
`from src.inventario import clasificar_stock`, y `src/__init__.py` es lo que lo hace
resoluble como paquete.

## Qué hace el workflow

`.github/workflows/ci.yml` corre el job `validar-python` en `ubuntu-latest` con Python 3.12:

| Step | Qué verifica | Si falla significa que… |
| --- | --- | --- |
| Descargar repositorio | `actions/checkout@v6` | El runner no pudo leer el repositorio. |
| Configurar Python | `actions/setup-python@v5` | La versión de Python pedida no está disponible. |
| Instalar dependencias | `pip install -r requirements.txt` | `requirements.txt` está roto o falta una dependencia. |
| Validar sintaxis | `python -m compileall src tests` | Hay un error de sintaxis que impide importar el módulo. |
| Ejecutar pruebas | `pytest -v` | La regla de negocio no se cumple. |

Se dispara con tres eventos:

- `push` a `main`
- `pull_request` hacia `main`
- `workflow_dispatch` (ejecución manual desde la pestaña Actions)

`run-name: CI ejecutado por ${{ github.actor }}` deja el nombre del usuario que disparó
la ejecución en el listado de Actions.

## Evidencias

Todas las capturas, enlaces a ejecuciones y respuestas a las preguntas de análisis están
en:

- [`docs/evidencias.md`](docs/evidencias.md) — ejecución exitosa, fallida, corregida,
  Pull Request con checks, ejecución manual y regla propia.
- [`docs/analisis.md`](docs/analisis.md) — respuestas a las 10 preguntas de la guía.

## Contexto

Esta práctica es la actividad preparatoria del Proyecto Final RapidGo 360. El aprendizaje
se traslada al repositorio del proyecto; este repositorio queda como evidencia del
ejercicio.
