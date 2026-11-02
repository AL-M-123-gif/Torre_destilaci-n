"""Ejecutar: python probar_bibliotecas.py (sin pip, sin internet)."""
from bibliotecas_torre import BibliotecaTorre
from preseleccion_torre import opciones_tuberia, opciones_brida, opciones_materiales, disponibilidad_precios
b=BibliotecaTorre()
print('Bibliotecas cargadas:',len(b.tablas))
t=opciones_tuberia(b, diametro_minimo_mm=100, espesor_nominal_minimo_mm=3.0)
assert t['recomendacion_preliminar'] is not None
print('Tubería (solo preselección):',t['recomendacion_preliminar']['nps'],t['recomendacion_preliminar']['schedule'])
f=opciones_brida(b,material_brida_id='SA182_F316L_FORJA',temperatura_diseno_C=130,
   presion_diseno_bar_g=3,nps='2')
assert f['recomendacion_preliminar'] is not None
print('Brida (solo preselección):',f['recomendacion_preliminar']['rating']['clase'])
assert opciones_materiales(b)['recomendacion_preliminar'] is None
assert not disponibilidad_precios(b)['aprobados_para_elegir_componente']
assert not b.tablas['cotizaciones']
print('PRUEBA CORRECTA: se bloqueó elección automática de materiales y precio comercial como aprobación normativa.')

assert b.tablas['demisters_opcionales'][0]['estado']=='rango_documental_no_aplicable_automaticamente'
