## Actualización de precios — 2 de noviembre de 2026 (v3)

- `bibliotecas/18_precios_publicados.csv` conserva las referencias históricas; ahora agrega los campos `estado_revision_precio` y `fecha_ultima_verificacion`. **Solo 14 referencias** fueron cotejadas de nuevo en la consulta del 2 de noviembre de 2026. El resto **no debe tratarse como revalidado**.
- `bibliotecas/25_cotizaciones_referenciales.csv` contiene **14 precios publicados** con fuente URL, unidad de compra, monto, IVA declarado y estado expreso `PRECIO_PUBLICADO_REFERENCIAL_NO_COTIZACION_FORMAL`. Los valores se revisaron en tiendas de México pero no garantizan suministro ni certificados; **no constituyen ofertas contractuales ni precios definitivos de torre**.
- `bibliotecas/12_cotizaciones.csv` permanece sin filas porque no se recibieron documentos de cotización formal; así no se fabrican cotizaciones ficticias.
- `ejemplos/K520/26_presupuesto_cotizaciones_referenciales.csv` asocia dos partidas específicas del ejemplo inicial a publicaciones coincidentes y mantiene sin precio los componentes de fabricación a medida. **No se calcula un costo total de la torre** con partidas incompletas.
- Dos vínculos de placas de inoxidable se reemplazaron por el catálogo del distribuidor, pues sus antiguas rutas individuales no eran consistentes con los títulos del producto. Para esas placas el IVA no ha sido confirmado.
- El importe de la placa de 8 mm, el de los platos especiales y el de la brida NPS 12 convertida desde USD no se incluyen como precios MXN confirmados.
- El lector ofrece `cotizaciones_referenciales()` e `importe_referencial(referencia_id, cantidad)`; **no** aprueba compras ni cumplimiento normativo automáticamente.

**Para GitHub:** subir todos los CSV, archivos `.py`, `MANIFIESTO.json` y carpetas preservando rutas. La versión de las tablas debe fijarse por commit/versión para obtener presupuestos reproducibles.

# Bibliotecas de Ingeniería — Diseño mecánico de torres de destilación

Paquete de prueba para integrar posteriormente a un cuaderno de Python/Google Colab.
**Fuente metodológica principal:** PDF de diseño mecánico de torres de destilación del profesor.
**Origen:** Bibliotecas_Torre_Destilacion_v7. Sin alterar datos originales ni inventar datos faltantes.

## Organización del repositorio

```
/
├── bibliotecas/                        # catálogos generales CSV (00-24) y ESTADO_COBERTURA.csv
├── ejemplos/K520/                       # cantidades y presupuesto de un caso, NO predeterminados
├── bibliotecas_torre.py                 # lector de catálogos
├── preseleccion_torre.py                # candidatas por dimensiones y ratings; NO aprueba ASME
├── verificar_bibliotecas.py            # pruebas de integridad de los catálogos
├── probar_bibliotecas.py               # prueba breve de consultas y preselecciones
└── MANIFIESTO.json                     # número de filas, versión y checksum SHA-256
```

### Cómo probar antes de conectar con Colab

1. Extraer el ZIP **completo** conservando subcarpetas.
2. Ejecutar `python verificar_bibliotecas.py` y `python probar_bibliotecas.py`.
3. No es necesario DWSIM para esta prueba de catálogos. El diseño completo queda para la futura integración al cuaderno de la torre.
4. Crear un repositorio y subir los archivos y subcarpetas tal como aparecen. El código futuro leerá este esquema.

## ¿Puede resolver automáticamente todo el diseño?

**No.** Esta es una versión de prueba de las bibliotecas. Existen tablas con datos suficientes para consultas limitadas: materiales 304/316, esfuerzos ASME con selección explícita de fila/notas, tuberías B36.19M, bridas Class 150 WN/RF y ratings grupo 2.3, costo base Turton para recipientes verticales y platos, y precios publicados como referencia.

Siguen sin datos numéricos universales: criterios hidráulicos específicos de los platos y factores A/B de presión externa. Las cotizaciones industriales formales y las entradas propias de una nueva simulación están vacías intencionalmente. El CEPCI 2026 está registrado sin valor numérico verificado en este paquete (no reemplazar con índices históricos). Las dimensiones de bridas solo se cubren en Class 150 WN RF; sin otras clases no se puede completar una comparación amplia.

### Cómo se recomienda la alternativa

**Dos etapas:** (1) filtrar por restricciones geométricas, P/T y reglas verificadas; (2) comparar candidatos por costo o masa *solo entre equivalentes realmente compatibles*. `preseleccion_torre.py` implementa filtros limitados, con información de faltantes. Una opción 'más barata' no se convierte en 'cumple ASME'.

- `opciones_tuberia`: filtra diámetro interior mínimo y espesor nominal mínimo aportados por el cálculo (este último debe incorporar tolerancias y márgenes). Ordena por diámetro exterior y espesor nominal, no por precio.
- `opciones_brida`: filtra ratings P–T y tamaños normalizados cargados, devuelve clases con datos geométricos disponibles; requiere validar material, bore, pernos, cargas externas, notas y UG-44.
- `opciones_materiales`: NO selecciona un grado por sí mismo: requiere compatibilidad química, temperaturas, tensión admisible y costo verificable.
- `disponibilidad_precios`: lista precios web como referencia; ninguno tiene aprobación automática de la especificación de diseño.

No debe presentarse ninguna preselección como certificación, aprobación normativa o dimensionamiento final.

## Ediciones/documentación y uso en GitHub

Los catálogos de dimensiones/esfuerzos proceden de documentos licenciados ASME de distintas ediciones (II-A/II-D 2019, VIII-1 2021, B16.5 2025, B36.19M 2004/R2015). **Recomendado: repositorio privado mientras no haya autorización para redistribuir extractos normativos.** No cargar PDFs licenciados en un repositorio público. La finalidad académica o ausencia de lucro no garantiza permiso para publicar las tablas extensas.

Las cotizaciones comerciales están fechadas; se deben volver a verificar. Turton contiene costos históricos (CEPCI base 397), no precios de adquisición 2026. `ejemplos/K520/` no se utilizará como valor predeterminado para otra torre ni sustituirá DWSIM o entrada manual.

## Integración posterior con Google Colab

Cuando se proporcione la URL del repositorio, configurar un descargador con versión o SHA comprobado: cargar primero bibliotecas, luego DWSIM o captura manual, y solo después iniciar cálculos. Para repositorios privados será necesaria autenticación autorizada o descarga manual del ZIP; los enlaces `raw.githubusercontent.com` sin credenciales no servirán.

> Los catálogos disponibles habilitan una prueba de selección, no garantizan el cálculo completo ni la aprobación ASME de una torre real.


## Actualización 02 nov 2026: GPSA e internos opcionales

Se incorporaron `23_demisters_opcionales.csv` y `24_metodos_gpsa.csv`; también se amplió `09_criterios_hidraulicos.csv`. La **sección 19 de GPSA** contiene correlaciones para la **torre de platos**, como la figura 19-13 (dependiente de espaciamiento y tensión superficial), mientras que la **sección 7** trata los **eliminadores de niebla** en separadores. No son métodos ni factores intercambiables.

Los coeficientes de las gráficas de platos no se inventaron ni se digitalizaron sin verificar. El futuro cuaderno solicitará los parámetros particulares si DWSIM no los proporciona; si no se puede consultar el gráfico aplicable, marcará el cálculo como pendiente. El uso de demister es **opcional** y NO se presupone para K-520.

**Privacidad / licencias:** mantener estas bibliotecas en un **repositorio privado** salvo contar con permiso suficiente para redistribuir los valores extraídos de ASME y GPSA. No subir a GitHub archivos PDF de esas publicaciones. Para Colab con repositorio privado será necesario acceder mediante un mecanismo autenticado (por ejemplo, token guardado como secreto de Colab) o subir una copia local del ZIP, nunca escribir tokens en el `.ipynb`.

El directorio `ejemplos/K520/` contiene únicamente datos preliminares del caso, no valores por defecto del programa. Los precios de catálogo no constituyen cotización formal.
