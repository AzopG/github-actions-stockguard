# Preguntas de análisis

Respuestas basadas en las ejecuciones de este repositorio. Los enlaces a cada run están
en [`evidencias.md`](evidencias.md).

## 1. Una ejecución exitosa y una fallida: ¿qué las produjo y qué step determinó el resultado?

**Exitosa:** run
[40704579086](https://github.com/AzopG/github-actions-stockguard/actions/runs/40704579086),
commit `af6fa18`. El cambio fue agregar `pytest.ini` con `pythonpath = .`. Lo determinó el
step **Ejecutar pruebas**: `5 passed in 0.03s`.

**Fallida:** run
[40704739441](https://github.com/AzopG/github-actions-stockguard/actions/runs/40704739441),
commit `885958c`. El cambio fue modificar una prueba para que esperara `NORMAL` donde la
regla produce `CRITICO`. También lo determinó el step **Ejecutar pruebas**, con
`1 failed, 4 passed` y exit code 1. Los cuatro steps anteriores terminaron en verde.

Hay una tercera: el run
[40704339348](https://github.com/AzopG/github-actions-stockguard/actions/runs/40704339348)
falló sin que yo lo provocara, por `ModuleNotFoundError: No module named 'src'`. El step
que falló fue el mismo, **Ejecutar pruebas**, pero la causa estaba en cómo pytest resuelve
el `sys.path`, no en la regla de negocio.

## 2. ¿Por qué ejecutar pytest localmente no reemplaza ejecutar pytest en GitHub Actions?

Porque no es el mismo entorno ni el mismo punto de entrada. En local corría Python 3.13.3
con pytest 9.2.0 instalado a mano en un `venv`; en el runner corre `ubuntu-latest` con
Python 3.12 y solo lo que declara `requirements.txt`.

Este repositorio lo demostró de la forma más incómoda:

```text
$ pytest -q
E   ModuleNotFoundError: No module named 'src'

$ python -m pytest -q
5 passed in 0.19s
```

Los mismos archivos, la misma máquina, resultados distintos según cómo se invoque pytest.
Yo había visto "5 passed" en local y el primer run en GitHub igual falló. Lo local prueba
que el código funciona **en mi máquina con mi configuración**; Actions prueba que el
repositorio, tal como está commiteado, es reproducible en una máquina limpia. Eso es
justamente lo que necesitan los otros dos integrantes del equipo.

## 3. ¿Qué riesgo tendría hacer merge a `main` sin esperar los checks del Pull Request?

Que el fallo se descubre después y lo paga todo el equipo. En este repositorio, `main` es
la base de todas las ramas: si el run 3 (la prueba con la expectativa incorrecta) se
hubiera mergeado, `main` quedaría en rojo y cada persona que abriera una rama nueva
partiría de una base rota, sin saber si el fallo es suyo o heredado.

El riesgo concreto no es "un check rojo", es perder la señal: con `main` en rojo nadie
puede distinguir un error propio de uno arrastrado. Por eso el PR debe exigir el check y
una aprobación antes del merge.

## 4. En la ejecución fallida, ¿cuál es la línea esencial del error y qué permitió diagnosticar?

```text
E       AssertionError: assert 'CRITICO' == 'NORMAL'
```

Esa línea dice tres cosas a la vez: el valor **real** fue `CRITICO`, el **esperado** era
`NORMAL`, y por lo tanto el defecto estaba en la expectativa de la prueba, no en la
función. La función devolvió lo que la regla de negocio prescribe para 7 unidades con
mínimo 20.

Lo que completó el diagnóstico fue el `tests/test_inventario.py:13` que pytest imprime
debajo (la línea exacta del `assert`) y el resumen `1 failed, 4 passed`: las otras cuatro
reglas seguían intactas, así que no había que sospechar de `clasificar_stock` entera.

## 5. ¿Qué diferencia hay entre un step que usa `uses:` y uno que usa `run:`?

`uses:` **ejecuta una acción reutilizable**: GitHub descarga ese componente y lo corre. En
este workflow, `actions/checkout@v6` descarga el repositorio y `actions/setup-python@v5`
prepara Python 3.12. Yo declaro qué herramienta quiero y con qué versión, pero no escribo
el código que la implementa.

`run:` **ejecuta comandos de shell** en el runner, en este caso sobre `ubuntu-latest` con
bash. `pip install -r requirements.txt`, `python -m compileall src tests` y `pytest -v` son
comandos míos, no acciones empaquetadas.

La diferencia práctica: `uses:` es "usá esta pieza ya hecha"; `run:` es "corré esto que
escribí". Un `run:` puede instalar cosas y fallar por cualquier motivo del sistema; un
`uses:` falla si la acción no existe, si la versión no existe o si su propio código falla.

## 6. ¿Qué aporta `${{ github.actor }}` en `run-name` y por qué sirve en equipo?

Aporta el usuario que disparó la ejecución. En este repositorio el listado de Actions se
lee como `CI ejecutado por AzopG` sin abrir el run.

En un equipo de tres sirve para dos cosas concretas: atribuir un fallo a un cambio sin
revisar el commit, y demostrar participación individual. El curso pide que cada integrante
ejecute el workflow manualmente una vez; con `github.actor` en el nombre, la ejecución
manual queda identificada por sí sola, sin capturas adicionales. Es la diferencia entre
"alguien corrió esto" y "lo corrió Luis el 29 de octubre".

## 7. Si el workflow pasa pero la aplicación completa falla en local con Docker, ¿Actions "no sirve"? ¿Qué verifica y qué no?

No. Verifica exactamente lo que el YAML le dice que verifique, y nada más.

Lo que sí verifica este workflow: que el código tenga sintaxis válida
(`compileall`), que las dependencias declaradas alcancen para importar el proyecto, y que
las cinco reglas de negocio se cumplan en una máquina Linux limpia con Python 3.12.

Lo que no verifica: que Kafka arranque, que el conector de Spark resuelva, que se pueda
escribir Parquet, ni que el pipeline produzca KPIs. Nada de eso está en el YAML.

Y hay evidencia de la semana anterior en el proyecto: `docker compose config --quiet`
pasaba mientras el broker moría al arrancar con `advertised.listeners cannot use the
nonroutable meta-address 0.0.0.0`. El check validaba **sintaxis** de YAML, no que el
servicio levante. Un verde significa "las condiciones que codifiqué se cumplen", no "el
sistema funciona". La conclusión no es que Actions no sirva, es que un check sin una
condición real detrás es decoración.

## 8. Tres checks para la variante de RapidGo 360

**a. `pytest` sobre las reglas puras de negocio** (clasificación del rating, umbrales de
A1 y A2, validación del contrato del evento).
Evita: que alguien cambie `3.60` por `3.50` en un umbral, o que `rating <= 3` deje de exigir
`complaint_reason`. Es un error que hoy no rompe nada visible: la alerta simplemente deja
de disparar.

**b. Validación del contrato de `samples/*.json` y del JSON que produce el producer.**
Evita: que un campo obligatorio desaparezca o cambie de tipo y Spark empiece a escribir
filas nulas sin lanzar excepción. Ya pasó con `samples/rating_event.json`, que por estar
indentado produjo 18 filas nulas en lugar de una.

**c. `python -m compileall` sobre `producer`, `spark`, `scripts` y `tests`.**
Evita: que un error de sintaxis en un job de Spark llegue a `main`. Sin esto, el error
aparece recién al correr el job dentro del contenedor, que tarda mucho más que un
`compileall` de dos segundos.

## 9. ¿Cuál de esos checks debería implementarse primero y por qué?

El **(a)**, las pruebas de reglas puras. Es el único que protege la integración de los
tres: sin él, un cambio en la lógica de umbrales puede pasar la revisión porque "compila y
corre", y el error se descubre cuando alguien mira un KPI que no cuadra. Además cuesta
segundos, no necesita Docker ni Kafka, y es determinista: siempre da el mismo resultado.

El (c) es el más barato y podría ir en el mismo workflow, en el mismo commit. El (b) exige
escribir primero las fixtures del contrato, así que es un paso más.

## 10. ¿Qué prueba sería demasiado costosa o frágil para cada push y cómo la validarías?

**Costosa:** levantar Kafka + Spark y correr el pipeline completo. Son minutos por
ejecución, hay que descargar el conector desde Maven, y en un repositorio privado consume
cuota rápido. Además el resultado depende de tiempos: una ventana de 10 minutos no se
emite si el watermark no la cerró.

**Frágil:** cualquier prueba sobre agregaciones con ventana y watermark. Que una ventana
salga o no depende de cuántos eventos llegaron y de cuándo se cerró; dos corridas con los
mismos datos pueden dar conteos distintos. Es la peor combinación: lenta y no
determinista.

**Cómo la validaría:** separada del CI de cada push, como evidencia local reproducible.
En RapidGo eso es lo que hace `python -m scripts.run_spark_job spark/streaming_job.py`
con `--degradation 0.7` y una salida concreta que se pega en el Issue. Si se quiere
automatizar, va en un workflow aparte con `workflow_dispatch` (o `schedule`), nunca en el
que bloquea cada PR.
