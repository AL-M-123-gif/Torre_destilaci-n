"""Preselección técnica orientativa. NUNCA interpreta aprobación ASME.

Separa selección geométrica/ratings de precios comerciales. Los precios web
registrados carecen de documentación suficiente para una compra normativa
automática y no se emplean como filtro de resistencia mecánica.
"""
from __future__ import annotations
from bibliotecas_torre import BibliotecaTorre, BibliotecaError


def opciones_tuberia(b: BibliotecaTorre, *, diametro_minimo_mm:float,
                      espesor_nominal_minimo_mm:float|None=None,
                      schedules_permitidos:tuple[str,...]|None=None):
    """Lista tuberías dimensionalmente candidatas según B36.19M.

    diametro_minimo_mm: mínimo hidráulico verificado por cálculo (mm).
    espesor_nominal_minimo_mm: umbral de ESPESOR NOMINAL ya corregido
    por tolerancia, corrosión, UG-45 y condiciones de carga cuando proceda.
    Si no se proporciona, no se evalúa espesor.
    """
    d=float(diametro_minimo_mm)
    if d<=0: raise BibliotecaError('Se requiere diámetro interior mínimo positivo (mm).')
    if espesor_nominal_minimo_mm is not None and float(espesor_nominal_minimo_mm)<=0:
        raise BibliotecaError('Espesor nominal mínimo debe ser positivo.')
    rows=b.tuberias(diametro_interior_min_mm=d)
    rows=[r for r in rows if schedules_permitidos is None or r['schedule'] in schedules_permitidos]
    if espesor_nominal_minimo_mm is not None:
        rows=[r for r in rows if float(r['espesor_nominal_mm'])>=float(espesor_nominal_minimo_mm)]
    rows.sort(key=lambda r:(float(r['diametro_exterior_mm']), float(r['espesor_nominal_mm'])))
    return {
        'estado':'PRESELECCION_DIMENSIONAL',
        'criterio_orden':'Menor diámetro exterior y luego menor espesor nominal entre opciones filtradas; NO equivale a mínimo costo',
        'candidatos':rows,
        'recomendacion_preliminar':rows[0] if rows else None,
        'faltantes_para_validacion':'Verificar tolerancias de manufactura, UG-45 completo, resistencia del material, conexiones y corrosión; cotizaciones separadas',
    }


def opciones_brida(b: BibliotecaTorre, *, material_brida_id:str,
                   temperatura_diseno_C:float,presion_diseno_bar_g:float,
                   nps:str,tipo:str='Welding Neck',cara:str='RF'):
    """Clase más baja con rating y dimensiones disponibles, únicamente como preselección.

    No incluye tensiones por esfuerzos externos, pernos, juntas, pasaje de
    cuello, certificaciones, compatibilidad química ni aceptación UG-44.
    """
    rates=b.ratings(material_brida_id,temperatura_diseno_C,
                    presion_diseno_bar_g=presion_diseno_bar_g)
    candidatos=[];no_catalogados=[]
    for r in rates:
        try:
            geo=b.geometria_brida(r['clase'],nps,tipo=tipo,cara=cara)
            candidatos.append({'rating':r,'geometria':geo})
        except BibliotecaError:
            no_catalogados.append(r['clase'])
    candidatos.sort(key=lambda r:int(r['rating']['clase']))
    return {
        'estado':'PRESELECCION_RATING_Y_DIMENSIONES',
        'candidatos':candidatos,
        'recomendacion_preliminar':candidatos[0] if candidatos else None,
        'clases_con_rating_pero_sin_dimensiones_cargadas':no_catalogados,
        'faltantes_para_validacion':'Notas B16.5, UG-44, bore/schedule, condiciones de junta/pernos, cargas externas, certificados y compatibilidad de servicio',
    }


def opciones_materiales(b: BibliotecaTorre,*,uso_propuesto:str|None=None):
    """Lista materiales; no selecciona el mejor sin corrosión, temperatura y costo."""
    rows=b.materiales()
    if uso_propuesto:rows=[r for r in rows if uso_propuesto.casefold() in r['uso_propuesto'].casefold()]
    return {'estado':'CANDIDATOS_SIN_CLASIFICACION','candidatos':rows,
        'recomendacion_preliminar':None,
        'faltantes_para_validacion':'Resistencia a corrosión, esfuerzo por forma y temperatura, notas ASME, costo y disponibilidad'}


def disponibilidad_precios(b: BibliotecaTorre,*,categoria:str|None=None):
    """Precios web consultables, nunca equivalencia mecánica comprobada."""
    a=b.precios_web(categoria=categoria)
    return {'estado':'SOLO_REFERENCIA_COMERCIAL','precios':a,
      'aprobados_para_elegir_componente':[],
      'advertencia':'Todos los registros web están marcados NO aptos para selección normativa automática; verificar equivalencia exacta, certificación y fecha.'}
