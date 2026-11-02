"""Consulta local de bibliotecas técnicas para diseño mecánico de torres.

No infiere propiedades faltantes, no elige filas ASME condicionadas ni convierte
un resultado de preselección en cumplimiento normativo.
No requiere librerías Python de terceros.
"""
from __future__ import annotations
import csv
from pathlib import Path
from fractions import Fraction

CATALOGOS={
 'fuentes':'00_fuentes_documentales.csv',
 'materiales':'01_materiales.csv',
 'esfuerzos':'02_esfuerzos_admisibles.csv',
 'propiedades_fisicas':'03_propiedades_fisicas.csv',
 'tuberias':'04_tuberias_b36_19m.csv',
 'materiales_bridas':'05_materiales_bridas.csv',
 'ratings_bridas':'06_ratings_bridas.csv',
 'dimensiones_bridas':'07_dimensiones_bridas.csv',
 'ug45':'08_ug45_minimos.csv',
 'hidraulica':'09_criterios_hidraulicos.csv',
 'presion_externa':'10_presion_externa.csv',
 'turton':'11_correlaciones_turton.csv',
 'cotizaciones':'12_cotizaciones.csv',
 'cepci':'13_indices_cepci.csv',
 'entradas_diseno':'14_entradas_diseno.csv',
 'formulas':'15_formulas_diseno.csv',
 'proveedores':'16_proveedores.csv',
 'factores_turton':'17_factores_turton.csv',
 'precios_web':'18_precios_publicados.csv',
 'parametros_comerciales':'19_parametros_comerciales.csv',
 'precios_exterior':'20_precios_internacionales_y_referencias.csv',
 'matriz_cotizacion':'21_matriz_partidas_y_cotizacion.csv',
 'fuentes_cotizacion':'22_fuentes_y_solicitudes_proveedores.csv',
 'demisters_opcionales':'23_demisters_opcionales.csv',
 'metodos_gpsa':'24_metodos_gpsa.csv',
  'cotizaciones_referenciales':'25_cotizaciones_referenciales.csv',
}

class BibliotecaError(ValueError):
    """No hay dato suficiente, o la consulta exige una decisión explícita."""

def _nps_numero(s):
    s=str(s).replace('≥','>=').strip()
    if s.startswith('>='): s=s[2:]
    tok=s.split()
    if len(tok)==2: return float(Fraction(tok[0]))+float(Fraction(tok[1]))
    return float(Fraction(s))

class BibliotecaTorre:
    def __init__(self,carpeta=None):
        self.carpeta=Path(carpeta) if carpeta is not None else Path(__file__).resolve().parent / 'bibliotecas'
        self.tablas={}
        for nombre,archivo in CATALOGOS.items():
            p=self.carpeta/archivo
            if not p.is_file():
                raise FileNotFoundError(f'Falta {archivo}. Utiliza la carpeta completa.')
            with p.open('r',newline='',encoding='utf-8-sig') as f:
                lector=csv.DictReader(f)
                if not lector.fieldnames:raise BibliotecaError(f'Sin encabezados: {archivo}')
                self.tablas[nombre]=list(lector)

    def cotizaciones_referenciales(self, *, categoria=None, proveedor=None):
        """Precios web para presupuestos preliminares, NO cotizaciones formales."""
        registros = list(self.tablas['cotizaciones_referenciales'])
        if categoria is not None:
            registros = [r for r in registros if r['categoria'].lower() == str(categoria).lower()]
        if proveedor is not None:
            registros = [r for r in registros if str(proveedor).lower() in r['proveedor'].lower()]
        return registros

    def importe_referencial(self, referencia_id, cantidad):
        """Costo bruto ilustrativo: unidades de catálogo, misma moneda, sin otros cargos."""
        q = float(cantidad)
        if q <= 0:
            raise BibliotecaError('La cantidad debe ser positiva.')
        opciones = [r for r in self.tablas['cotizaciones_referenciales']
                    if r['referencia_id'] == referencia_id]
        if len(opciones) != 1:
            raise BibliotecaError('Referencia inexistente o duplicada.')
        r = opciones[0]
        return {'referencia_id': referencia_id, 'cantidad': q,
                'unidad': r['unidad_venta'], 'moneda': r['moneda'],
                'importe_referencial': round(q * float(r['precio_unitario']), 2),
                'estado': 'REFERENCIAL_NO_COTIZACION_FORMAL',
                'advertencia': r['limitacion_para_diseno']}

    def precios_web(self, *, categoria=None, proveedor=None):
        """Precios observados; no sustituyen cotizaciones formales ni validan ASME."""
        items=self.tablas['precios_web']
        if categoria is not None:items=[r for r in items if r['categoria']==categoria]
        if proveedor is not None:items=[r for r in items if r['proveedor']==proveedor]
        return list(items)

    def partidas_pendientes(self):
        return [r for r in self.tablas['matriz_cotizacion'] if r['precio_de_costo_verificado_para_especificacion_final']=='NO']

    def precios_fuera_mxn(self):
        return list(self.tablas['precios_exterior'])

    def ficha_comercial(self, registro_id):
        """Atributos comerciales del SKU, aislados de la biblioteca normativa."""
        return [r for r in self.tablas['parametros_comerciales'] if r['registro_id']==registro_id]

    def materiales(self):
        return [{k:r[k] for k in ('material_id','especificacion','grado','uns','forma_producto','estado')}
                for r in self.tablas['materiales']]

    def tabulados(self,nombre):
        if nombre not in self.tablas:raise BibliotecaError(f'Catálogo desconocido: {nombre}')
        return list(self.tablas[nombre])

    def opciones_esfuerzo(self,material_id,temperatura_C):
        t=float(temperatura_C)
        if not 0<=t<=450:
            raise BibliotecaError('Solo se han incorporado temperaturas de 40 a 450 °C. Para temperaturas menores a 0 °C consultar requisitos de MDMT y tablas pertinentes; no extrapolar >450 °C.')
        datos=[r for r in self.tablas['esfuerzos'] if r['material_id']==material_id]
        if not datos:raise BibliotecaError(f'No hay esfuerzo tabulado para {material_id}')
        opciones=[]
        for fila in sorted({int(r['fila_asme']) for r in datos}):
            vals=sorted([r for r in datos if int(r['fila_asme'])==fila and float(r['temperatura_limite_C'])>=t],
                        key=lambda r:float(r['temperatura_limite_C']))
            if vals:
                r=vals[0]
                opciones.append(dict(material_id=material_id,fila_asme=fila,
                    temperatura_limite_C=float(r['temperatura_limite_C']),
                    esfuerzo_admisible_MPa=float(r['esfuerzo_admisible_MPa']),
                    notas_asme=r['notas_asme'],presion_externa_grafica=r['presion_externa_grafica'],
                    fuente=r['fuente'],edicion=r['edicion'],pagina_pdf=r['pagina_pdf'],
                    advertencia='Seleccionar la fila aplicable tras revisar las notas; no aprobación automática'))
        if not opciones:raise BibliotecaError('Sin renglón aplicable en el intervalo tabulado')
        return opciones

    def esfuerzo(self,material_id,temperatura_C,*,fila_asme=None):
        ops=self.opciones_esfuerzo(material_id,temperatura_C)
        if fila_asme is None:
            raise BibliotecaError(f'Selecciona fila_asme después de revisar las notas: {[(o["fila_asme"],o["esfuerzo_admisible_MPa"]) for o in ops]}')
        m=[x for x in ops if x['fila_asme']==int(fila_asme)]
        if len(m)!=1:raise BibliotecaError('Fila ASME no encontrada o no aplicable')
        return m[0]

    def propiedad(self,material_id,propiedad,temperatura_C=None):
        rows=[r for r in self.tablas['propiedades_fisicas'] if r['material_id']==material_id and r['propiedad']==propiedad]
        if not rows:raise BibliotecaError('No hay propiedad disponible para material y tipo solicitados')
        const=[r for r in rows if not r['temperatura_C']]
        if const:
            if len(const)!=1:raise BibliotecaError('Hay múltiples constantes para la misma propiedad')
            r=const[0];return dict(valor=float(r['valor']),unidad=r['unidad'],temperatura_tabla_C=None,
                                     fuente=r['fuente'],estado=r['estado'],notas=r['notas'])
        if temperatura_C is None:raise BibliotecaError('Debes indicar temperatura en °C')
        t=float(temperatura_C)
        minimum=min(float(r['temperatura_C']) for r in rows)
        maximum=max(float(r['temperatura_C']) for r in rows)
        if not minimum<=t<=maximum:raise BibliotecaError('Temperatura fuera de las propiedades tabuladas: no se extrapola')
        cand=sorted([r for r in rows if float(r['temperatura_C'])>=t],key=lambda r:float(r['temperatura_C']))
        r=cand[0]
        return dict(valor=float(r['valor']),unidad=r['unidad'],temperatura_tabla_C=float(r['temperatura_C']),
                    fuente=r['fuente'],estado=r['estado'],notas=r['notas'])

    def tuberias(self,*,schedule=None,nps=None,diametro_interior_min_mm=None):
        a=self.tablas['tuberias']
        if schedule is not None:a=[r for r in a if r['schedule'].upper()==str(schedule).upper()]
        if nps is not None:a=[r for r in a if abs(_nps_numero(r['nps'])-_nps_numero(nps))<1e-9]
        if diametro_interior_min_mm is not None:
            a=[r for r in a if float(r['diametro_interior_calculado_mm'])>=float(diametro_interior_min_mm)]
        return sorted(a,key=lambda r:(float(r['diametro_interior_calculado_mm']),float(r['espesor_nominal_mm'])))

    def ug45_minimo(self,nps):
        d=_nps_numero(nps)
        if d>=12: dkey='>=12'
        else:
            dkey=next((r['nps'] for r in self.tablas['ug45'] if r['nps']!='>=12' and abs(_nps_numero(r['nps'])-d)<1e-9),None)
            if dkey is None:raise BibliotecaError('UG-45 requiere NPS estándar tabulado, o equivalente mayor para un diámetro exterior no estándar')
        r=next(r for r in self.tablas['ug45'] if r['nps']==dkey)
        return dict(nps_tabla=dkey,minimo_tabla_ug45_mm=float(r['minimo_tabla_ug45_mm']),
                    fuente=r['fuente'],edicion=r['edicion'],advertencia='Mínimo tabulado; aplicar cálculo completo UG-45, CA y nota de UG-16(d)')

    def ratings(self,material_brida_id,temperatura_C,*,presion_diseno_bar_g=None):
        mats=[r for r in self.tablas['materiales_bridas'] if r['material_brida_id']==material_brida_id]
        if len(mats)!=1:raise BibliotecaError('Material de brida no identificado de forma única')
        t=float(temperatura_C)
        if not 38<=t<=454:raise BibliotecaError('Temperatura fuera de rango 38-454 °C cargado. No extrapolar, revisar notas B16.5.')
        grupo=mats[0]['grupo_asme_b165']
        rows=[r for r in self.tablas['ratings_bridas'] if r['grupo_asme_b165']==grupo]
        opciones=[]
        for cls in sorted({int(r['clase']) for r in rows}):
            cand=sorted([r for r in rows if int(r['clase'])==cls and float(r['temperatura_limite_C'])>=t],
                        key=lambda r:float(r['temperatura_limite_C']))
            if not cand:continue
            r=cand[0]
            if presion_diseno_bar_g is not None and float(r['presion_max_bar_g'])<float(presion_diseno_bar_g):continue
            opciones.append(dict(clase=cls,temperatura_limite_C=float(r['temperatura_limite_C']),
                                 presion_max_bar_g=float(r['presion_max_bar_g']),fuente=r['fuente'],
                                 estado=r['estado'],advertencia='Validar notas, geometría disponible, brida y presión manométrica'))
        return opciones

    def geometria_brida(self,clase,nps,*,tipo='Welding Neck',cara='RF'):
        a=[r for r in self.tablas['dimensiones_bridas'] if r['clase']==str(clase) and
           abs(_nps_numero(r['nps'])-_nps_numero(nps))<1e-9 and
           r['tipo'].casefold()==tipo.casefold() and r['cara'].casefold()==cara.casefold()]
        if len(a)!=1:raise BibliotecaError('Esta geometría Class/NPS/tipo/cara no está cargada')
        return a[0]

    def proveedores(self,categoria=None,estado=None):
        """Lista potenciales proveedores. No devuelve precios no cotizados."""
        rows=self.tablas['proveedores']
        if categoria: rows=[r for r in rows if r['categoria']==categoria]
        if estado: rows=[r for r in rows if r['estado']==estado]
        return list(rows)

    def costo_base_turton(self,equipo,capacidad):
        """USD de 2001: Eq. A.1 de Turton. Valida límites de correlación.

        No implica cotización ni actualiza CEPCI ni calcula bare module.
        """
        import math
        rows=[r for r in self.tablas['turton'] if r['equipo']==equipo]
        if len(rows)!=1:raise BibliotecaError('No existe correlación Turton para el equipo solicitado')
        r=rows[0]; a=float(capacidad)
        if not float(r['limite_min'])<=a<=float(r['limite_max']):
            raise BibliotecaError(f'Capacidad {a} fuera de [{r["limite_min"]}, {r["limite_max"]}] {r["unidad_variable"]}; no extrapolar')
        loga=math.log10(a)
        base=10**(float(r['K1'])+float(r['K2'])*loga+float(r['K3'])*loga*loga)
        return {'equipo':equipo,'capacidad':a,'unidad_capacidad':r['unidad_variable'],
                'costo_base_USD_2001':base,'CEPCI_base':397.0,'factor_precio':None,
                'nota':'Costo comprado base: sin FM, FP, FBM, Fq, CEPCI actual ni cotización'}

    @staticmethod
    def factor_presion_turton_vasija(presion_manometrica_bar,diametro_m):
        """Turton 4th ed., Appendix A Eq. A.2: factor económico, no cálculo UG-28.
        Se restringe aquí a D 0.3-4.0 m, ámbito señalado en la referencia.
        """
        p=float(presion_manometrica_bar); d=float(diametro_m)
        if not 0.3<=d<=4:raise BibliotecaError('Revisar aplicación del factor de presión Turton: D fuera de 0.3 a 4.0 m')
        if p<=-1:raise BibliotecaError('La presión manométrica no puede ser <= -1 bar en esta correlación')
        if p < -0.5: return 1.25
        t=((p+1)*d)/(2*(850-0.6*(p+1)))+0.00315
        return max(1.0,t/0.0063)

    def costo_bare_module_turton(self,equipo,capacidad,*,factor_material=None,
                                  factor_presion=None,numero_platos=None,
                                  factor_cantidad=None,factor_bm_platos=None,
                                  cepci_actual=None):
        """Calcula Bare Module solo con factores explícitos y comprobados.
        Para torre: CBM=CP0*(B1+B2*FM*FP).
        Para platos: CBM=CP0*N*Fq*FBM_platos.
        """
        b=self.costo_base_turton(equipo,capacidad)
        cp=b['costo_base_USD_2001']
        if equipo=='recipiente_vertical':
            if factor_material is None or factor_presion is None:
                raise BibliotecaError('Faltan FM y FP para calcular el bare module del recipiente')
            vals=[float(factor_material),float(factor_presion)]
            if any(x<=0 for x in vals):raise BibliotecaError('FM y FP deben ser positivos')
            r=next(r for r in self.tablas['turton'] if r['equipo']==equipo)
            fbm=float(r['B1'])+float(r['B2'])*vals[0]*vals[1]
            cbm=cp*fbm
        elif equipo in {'plato_perforado','plato_valvulas'}:
            if any(x is None for x in [numero_platos,factor_cantidad,factor_bm_platos]):
                raise BibliotecaError('Se requieren N, Fq y FBM_platos verificados para los platos')
            n=int(numero_platos);fq=float(factor_cantidad);fbm=float(factor_bm_platos)
            if n<=0 or fq<=0 or fbm<=0:raise BibliotecaError('N, Fq y FBM deben ser positivos')
            cbm=cp*n*fq*fbm
        else:raise BibliotecaError('Equipo no soportado para bare module')
        b['costo_bare_module_USD_2001']=cbm
        if cepci_actual is not None:
            ind=float(cepci_actual)
            if ind<=0:raise BibliotecaError('Índice CEPCI actual inválido')
            b['costo_bare_module_USD_actualizado']=cbm*ind/397.0
            b['CEPCI_actual']=ind
        else:b['costo_bare_module_USD_actualizado']=None
        return b
