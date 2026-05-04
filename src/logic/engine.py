import pandas as pd

class KardexEngine:
    def __init__(self, data_dict):
        self.articulos = data_dict['ARTICULOS']
        self.almacenes = data_dict['ALMACENES']
        self.movimientos = data_dict['MOVIMIENTOS']
        self.saldos_iniciales = data_dict['SALDOS_INICIALES']
        self.movimientos['Fecha'] = pd.to_datetime(self.movimientos['Fecha'])
        self.movimientos = self.movimientos.sort_values(by='Fecha')

    def process_kardex_detallado(self):
        # Estado inicial {(alm, sku): {'cant': X, 'costo': Y}}
        estado = {(f['Cod_Almacen'], f['Cod_Articulo']): {'cant': f['Cantidad_Inicial'], 'costo': f['Costo_Unitario_Inicial']} 
                  for _, f in self.saldos_iniciales.iterrows()}
        kardex_filas = []

        for _, mov in self.movimientos.iterrows():
            sku = mov['Cod_Articulo']
            op = str(mov['Cod_Operacion']).zfill(2)
            cant_mov = mov['Cantidad']
            costo_referencia = 0

            # --- PROCESAR SALIDA (Origen) ---
            if pd.notna(mov['Cod_Almacen_Origen']):
                alm_orig = mov['Cod_Almacen_Origen']
                st_orig = estado.get((alm_orig, sku), {'cant': 0, 'costo': 0})
                costo_referencia = st_orig['costo'] # Capturamos el costo para transferencias
                st_orig['cant'] -= cant_mov
                estado[(alm_orig, sku)] = st_orig
                kardex_filas.append(self._crear_fila_kardex(mov, alm_orig, 'SALIDA', cant_mov, costo_referencia, st_orig))

            # --- PROCESAR INGRESO (Destino) ---
            if pd.notna(mov['Cod_Almacen_Destino']):
                alm_dest = mov['Cod_Almacen_Destino']
                st_dest = estado.get((alm_dest, sku), {'cant': 0, 'costo': 0})
                
                # Definir costo de entrada
                costo_in = mov['Costo_Unitario_Origen'] if op == '02' else costo_referencia
                
                # Fórmula de Promedio Ponderado
                n_cant = st_dest['cant'] + cant_mov
                if n_cant > 0:
                    st_dest['costo'] = ((st_dest['cant'] * st_dest['costo']) + (cant_mov * costo_in)) / n_cant
                st_dest['cant'] = n_cant
                estado[(alm_dest, sku)] = st_dest
                kardex_filas.append(self._crear_fila_kardex(mov, alm_dest, 'INGRESO', cant_mov, costo_in, st_dest))

        return pd.DataFrame(kardex_filas)

    def process_kardex_consolidado(self):
        # Cálculo de Saldo Inicial Consolidado (Promedio Ponderado Real)
        df_ini = self.saldos_iniciales.copy()
        df_ini['Valor_Ini'] = df_ini['Cantidad_Inicial'] * df_ini['Costo_Unitario_Inicial']
        res_ini = df_ini.groupby('Cod_Articulo').agg({'Cantidad_Inicial': 'sum', 'Valor_Ini': 'sum'})
        
        estado_c = {sku: {'cant': r['Cantidad_Inicial'], 'costo': r['Valor_Ini']/r['Cantidad_Inicial'] if r['Cantidad_Inicial'] > 0 else 0} 
                    for sku, r in res_ini.iterrows()}
        
        kardex_c_filas = []
        for _, mov in self.movimientos.iterrows():
            sku = mov['Cod_Articulo']
            op = str(mov['Cod_Operacion']).zfill(2)
            if op == '11': continue # Ignorar traslados internos para SUNAT
            
            st = estado_c.get(sku, {'cant': 0, 'costo': 0})
            tipo = 'INGRESO' if op == '02' else 'SALIDA'
            val_unit = mov['Costo_Unitario_Origen'] if op == '02' else st['costo']
            
            if tipo == 'INGRESO':
                n_cant = st['cant'] + mov['Cantidad']
                st['costo'] = ((st['cant'] * st['costo']) + (mov['Cantidad'] * val_unit)) / n_cant
                st['cant'] = n_cant
            else:
                st['cant'] -= mov['Cantidad']

            estado_c[sku] = st
            kardex_c_filas.append(self._crear_fila_kardex(mov, 'CONSOLIDADO', tipo, mov['Cantidad'], val_unit, st))
        return pd.DataFrame(kardex_c_filas)

    def _crear_fila_kardex(self, mov, almacen, tipo, cant, unit, st):
        return {
            'Almacen': almacen, 'Fecha': mov['Fecha'], 'Articulo': mov['Cod_Articulo'],
            'Tipo_Op': mov['Cod_Operacion'], 'Movimiento': tipo, 'Cant': cant,
            'Costo_Unit': unit, 'Total_Mov': cant * unit, 'Saldo_Cant': st['cant'],
            'Saldo_Costo_Prom': st['costo'], 'Saldo_Valor_Total': st['cant'] * st['costo']
        }