# Cómo subir bibliotecas a GitHub

1. Descomprime **Bibliotecas_Torre_Destilacion_GitHub_2026_v3_Precios.zip** en tu equipo.
2. En GitHub elige **New repository** con un nombre como `bibliotecas-torre-destilacion`.
3. Selecciona **Private** porque varios catálogos derivan de documentos con licencia.
4. Crea el repositorio, entra y usa **Add file > Upload files**.
5. Arrastra **todo el contenido de la carpeta descomprimida** (archivos `.py`, `.md`, `.json` y carpetas `bibliotecas/` y `ejemplos/`). No arrastres solamente el `.zip` o los CSV sueltos.
6. Confirma los cambios con el mensaje `Bibliotecas iniciales de torre de destilacion`.
7. Verifica que aparezcan `bibliotecas/04_tuberias_b36_19m.csv`, `bibliotecas/09_criterios_hidraulicos.csv`, `bibliotecas/24_metodos_gpsa.csv`, `bibliotecas/25_cotizaciones_referenciales.csv`, `bibliotecas_torre.py`, `preseleccion_torre.py` y `MANIFIESTO.json`.
8. Comparte el enlace del repositorio para generar el cuaderno Colab que lea las bibliotecas (si el repositorio es privado, no compartas una contraseña ni un token en el chat).

**Pruebas locales (opcional):** `python verificar_bibliotecas.py` y `python probar_bibliotecas.py`.

**Importante:** no publiques los libros PDF ASME, GPSA o Turton junto con estos archivos.
