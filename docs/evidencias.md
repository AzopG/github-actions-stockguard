# Evidencias de ejecución

Repositorio: https://github.com/AzopG/github-actions-stockguard

Todas las ejecuciones corresponden al workflow **CI StockGuard** (`.github/workflows/ci.yml`),
job `validar-python`, runner `ubuntu-latest`, Python 3.12.

## Resumen de ejecuciones

| # | Run | Commit | Evento | Resultado | Qué la produjo |
| --- | --- | --- | --- | --- | --- |
| 1 | [40704339348](https://github.com/AzopG/github-actions-stockguard/actions/runs/40704339348) | `8a9c2f9` | `push` a `main` | ❌ failure | Primera subida del workflow. `ModuleNotFoundError: No module named 'src'`. |
| 2 | [40704579086](https://github.com/AzopG/github-actions-stockguard/actions/runs/40704579086) | `af6fa18` | `push` a `main` | ✅ success | Corrección real: `pytest.ini` con `pythonpath = .`. |
| 3 | [40704739441](https://github.com/AzopG/github-actions-stockguard/actions/runs/40704739441) | `885958c` | `push` a `main` | ❌ failure | **Fallo intencional**: una prueba espera `NORMAL` donde corresponde `CRITICO`. |
| 4 | [40704911781](https://github.com/AzopG/github-actions-stockguard/actions/runs/40704911781) | `c33b495` | `push` a `main` | ✅ success | Se restaura la expectativa correcta. |
| 5 | [40705250794](https://github.com/AzopG/github-actions-stockguard/actions/runs/40705250794) | `554b4fc` | `pull_request` (PR #1) | ✅ success | Regla de sobrestock y sus pruebas, antes del merge. |
| 6 | [40705412058](https://github.com/AzopG/github-actions-stockguard/actions/runs/40705412058) | `c33b495` | `workflow_dispatch` | ✅ success | Ejecución manual desde la cuenta `AzopG`. |

## Ejecución exitosa (run 2)

- Commit: `af6fa18` — `ci: add pytest.ini so pytest finds the src package`.
- Determina el resultado el step **Ejecutar pruebas**.
- Salida:

  ```text
  collected 5 items
  tests/test_inventario.py::test_stock_agotado PASSED                      [ 20%]
  tests/test_inventario.py::test_stock_critico PASSED                      [ 40%]
  tests/test_inventario.py::test_stock_bajo PASSED                         [ 60%]
  tests/test_inventario.py::test_stock_normal PASSED                       [ 80%]
  tests/test_inventario.py::test_stock_invalido PASSED                     [100%]

  ============================== 5 passed in 0.03s ==============================
  ```

- Nombre de la ejecución: `CI ejecutado por AzopG`, gracias a
  `run-name: CI ejecutado por ${{ github.actor }}`.

## Ejecución fallida (run 3, provocada)

Cambio en `tests/test_inventario.py`:

```python
def test_stock_critico():
    assert clasificar_stock(7, 20) == "NORMAL"  # cambio incorrecto intencional
```

- Commit: `885958c` — `test: provocar fallo controlado de CI`.
- Step que falló: **Ejecutar pruebas**. Los steps previos terminaron correctamente.
- Línea esencial del error:

  ```text
  E       AssertionError: assert 'CRITICO' == 'NORMAL'
  ```

- Resumen: `1 failed, 4 passed in 0.03s` y `Process completed with exit code 1`.

## Ejecución corregida (run 4)

- Commit: `c33b495` — `test: restaurar la expectativa correcta de stock critico`.
- Resultado: `5 passed`, workflow en verde.

## Pull Request con checks

- PR: https://github.com/AzopG/github-actions-stockguard/pull/1
- Rama: `feature/alerta-sobrestock` → `main`
- Commit: `554b4fc` — `feat: agregar regla de sobrestock`
- Check: `validar-python` → **pass**, 8 s.
- El workflow se ejecutó por el evento `pull_request`, no por `push`: el trigger de `push`
  está limitado a `main`.
- Pruebas en el PR: `10 passed` (5 originales + 5 de la regla nueva).
- Merge con squash: `0fea355`. El `push` resultante a `main` volvió a correr el workflow en
  verde (run
  [40705766562](https://github.com/AzopG/github-actions-stockguard/actions/runs/40705766562)).

## Ejecución manual

- Comando: `gh workflow run ci.yml --ref main`
- Run: https://github.com/AzopG/github-actions-stockguard/actions/runs/40705412058
- Evento registrado: `workflow_dispatch`, disparado por `AzopG`.
- Resultado: ✅ success en 18 s.

## Regla propia y pruebas

- Función: `detectar_sobrestock(stock_actual, stock_minimo, factor=2.0)` en
  [`src/inventario.py`](../src/inventario.py).
- Pruebas: [`tests/test_inventario.py`](../tests/test_inventario.py).
- Commit: `554b4fc`; Pull Request: https://github.com/AzopG/github-actions-stockguard/pull/1

## Primer fallo, no intencional (run 1)

Vale la pena conservarlo porque es el caso que la guía lista en "Problemas frecuentes":
`ModuleNotFoundError: src`. `src/__init__.py` existía y `pytest` se ejecutaba desde la
raíz, pero el script de consola `pytest` no agrega la raíz del repositorio a `sys.path`:
agrega el directorio del test (`tests/`). La diferencia se reproduce en local:

```text
$ pytest -q
E   ModuleNotFoundError: No module named 'src'

$ python -m pytest -q
5 passed in 0.19s
```

La solución no fue cambiar el workflow, sino `pytest.ini` con `pythonpath = .`, para que
ambas formas de invocar pytest se comporten igual en local y en el runner.
