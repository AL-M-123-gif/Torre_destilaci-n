"""Pruebas reproducibles del paquete de catálogos (no de cumplimiento ASME)."""
from pathlib import Path
from bibliotecas_torre import BibliotecaTorre, BibliotecaError, _nps_numero
b=BibliotecaTorre(Path(__file__).parent / 'bibliotecas')
assert len(b.tablas)==26,len(b.tablas)
mats={r['material_id'] for r in b.tablas['materiales']}
assert len(mats)==len(b.tablas['materiales'])
for col,key in [('esfuerzos','material_id'),('propiedades_fisicas','material_id'),('presion_externa','material_id')]:
 for r in b.tablas[col]:assert r[key] in mats,(col,r[key])
for col,keys in {
 'esfuerzos':['material_id','fila_asme','temperatura_limite_C'],
 'tuberias':['nps','schedule'],
 'propiedades_fisicas':['material_id','propiedad','temperatura_C'],
 'ratings_bridas':['grupo_asme_b165','clase','temperatura_limite_C'],
 'dimensiones_bridas':['clase','tipo','cara','nps'],
 'ug45':['nps']}.items():
 seen=set()
 for r in b.tablas[col]:
  key=tuple(r[k] for k in keys)
  assert key not in seen,('clave duplicada',col,key)
  seen.add(key)
for r in b.tablas['esfuerzos']:
 assert float(r['esfuerzo_admisible_MPa'])>0
 assert float(r['temperatura_limite_C'])<=float(r['temperatura_max_servicio_viii1_C'])
for r in b.tablas['tuberias']:
 assert float(r['espesor_nominal_mm'])>0
 assert abs(float(r['diametro_interior_calculado_mm'])-
    (float(r['diametro_exterior_mm'])-2*float(r['espesor_nominal_mm'])))<0.00001
for r in b.tablas['dimensiones_bridas']:
 assert int(r['numero_pernos'])>0
 assert float(r['od_brida_mm'])>float(r['diametro_circulo_pernos_mm'])
assert {round(o['esfuerzo_admisible_MPa'],1) for o in b.opciones_esfuerzo('SA240_316L_PLACA',130)}=={115.,87.4}
assert b.esfuerzo('SA240_316L_PLACA',130,fila_asme=7)['esfuerzo_admisible_MPa']==87.4
assert {round(o['esfuerzo_admisible_MPa'],1) for o in b.opciones_esfuerzo('SA240_304L_PLACA',130)}=={115.,88.1}
assert b.ug45_minimo('12')['minimo_tabla_ug45_mm']==8.34
assert b.ug45_minimo('1/2')['minimo_tabla_ug45_mm']==2.42
assert b.propiedad('SA240_316L_PLACA','densidad')['valor']==8030
assert b.propiedad('SA240_316L_PLACA','modulo_elasticidad',130)['valor']==186000
assert len(b.tuberias(nps='12',schedule='40S'))==1
assert b.tuberias(nps='12',schedule='40S')[0]['espesor_nominal_mm']=='9.53'
assert b.tuberias(nps='12',schedule='40S')[0]['diametro_exterior_mm']=='323.9'
assert b.geometria_brida(150,'12')['diametro_circulo_pernos_mm']=='431.8'
assert len(b.ratings('SA182_F316L_FORJA',130,presion_diseno_bar_g=3))==7
assert b.ratings('SA182_F316L_FORJA',130,presion_diseno_bar_g=3)[0]['presion_max_bar_g']==12.1
assert not b.tablas['cotizaciones'] and len(b.tablas['cepci'])==13
assert len(b.tablas['cotizaciones_referenciales'])==14
assert b.importe_referencial('CREF-004',2)['importe_referencial']==2198.00
for test in [lambda:b.esfuerzo('SA240_316L_PLACA',130),
             lambda:b.opciones_esfuerzo('SA240_316L_PLACA',800),
             lambda:b.propiedad('SA240_316L_PLACA','modulo_elasticidad',900),
             lambda:b.ug45_minimo('7'),
             lambda:b.geometria_brida(300,'12'),
             lambda:b.ratings('SA182_F316L_FORJA',800)]:
 try:test();raise AssertionError('Se esperaba un error de catálogo/selección')
 except BibliotecaError:pass
assert len(b.proveedores())==12
assert abs(b.costo_base_turton('recipiente_vertical',22.6195)['costo_base_USD_2001']-20041.20)<1
assert abs(b.costo_base_turton('plato_perforado',1.13097)['costo_base_USD_2001']-1046.88)<1
assert b.factor_presion_turton_vasija(-0.8,1.2)==1.25
for test in [lambda:b.costo_bare_module_turton('recipiente_vertical',22.6195),lambda:b.costo_base_turton('plato_valvulas',0.1)]:
 try:test();raise AssertionError('Error esperado por entrada incompleta o extrapolación')
 except BibliotecaError:pass
print('VERIFICACIÓN CORRECTA. Catálogos:',len(b.tablas))
for category,rows in b.tablas.items():print(f'{category:22s} {len(rows):4d} registros')

# Precios publicados no se confunden con cotizaciones formales ni con propiedades ASME.
assert not b.tablas['cotizaciones']
assert len(b.precios_web())==39
assert all(r['tipo_precio'].startswith('Precio web') and r['apto_seleccion_normativa_automatica']=='NO' for r in b.precios_web())
assert len(b.ficha_comercial('WEB-007'))==9
assert len({r['registro_id'] for r in b.precios_web()})==len(b.precios_web())

# Asegurar unicidad, fuente y no uso de precios como validacion ASME.
assert all(r["apto_seleccion_normativa_automatica"] == "NO" for r in b.precios_web())
assert all(r["precio_publicado_MXN"] and r["url_fuente"] for r in b.precios_web())
assert len(b.tablas["matriz_cotizacion"]) == 22
assert len(b.tablas["fuentes_cotizacion"]) == 15

# GPSA §19 (platos) y §7 (demisters) se mantienen separados.
assert any(r['aplicacion']=='TORRE_DE_PLATOS' for r in b.tablas['metodos_gpsa'])
assert all(r['familia']=='demister' for r in b.tablas['demisters_opcionales'])
assert not any(r['familia_interno']=='demister' for r in b.tablas['hidraulica'])
