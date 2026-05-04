import pandas as pd

class InventoryValidator:
    def __init__(self, df_kardex_detallado, df_kardex_consolidado):
        self.detallado = df_kardex_detallado
        self.consolidado = df_kardex_consolidado

    def check_inconsistencies(self):
        """
        Compara la sumatoria de saldos finales de almacenes individuales 
        contra el saldo final del reporte consolidado.
        """
        # 1. Obtener el último saldo de cada artículo en cada almacén
        saldos_finales_almacenes = self.detallado.sort_values('Fecha').groupby(['Almacen', 'Articulo']).tail(1)
        
        # 2. Sumar los saldos de todos los almacenes por artículo
        resumen_almacenes = saldos_finales_almacenes.groupby('Articulo').agg({
            'Saldo_Cant': 'sum',
            'Saldo_Valor_Total': 'sum'
        }).reset_index()
        resumen_almacenes.columns = ['Articulo', 'Suma_Cant_Alms', 'Suma_Valor_Alms']

        # 3. Obtener el saldo final del reporte consolidado
        resumen_consolidado = self.consolidado.sort_values('Fecha').groupby('Articulo').tail(1)
        resumen_consolidado = resumen_consolidado[['Articulo', 'Saldo_Cant', 'Saldo_Valor_Total']]
        resumen_consolidado.columns = ['Articulo', 'Cant_Consol', 'Valor_Consol']

        # 4. Cruzar ambos resultados para comparar
        comparativa = pd.merge(resumen_almacenes, resumen_consolidado, on='Articulo', how='outer').fillna(0)

        # 5. Calcular diferencias
        comparativa['Dif_Cant'] = comparativa['Suma_Cant_Alms'] - comparativa['Cant_Consol']
        comparativa['Dif_Valor'] = comparativa['Suma_Valor_Alms'] - comparativa['Valor_Consol']

        # Identificar inconsistencias (usando un margen pequeño por decimales)
        inconsistencias = comparativa[
            (comparativa['Dif_Cant'].abs() > 0.001) | 
            (comparativa['Dif_Valor'].abs() > 0.01)
        ]

        return inconsistencias, comparativa

    def get_summary_alerts(self, inconsistencias):
        """Genera mensajes de alerta para la interfaz de usuario."""
        if inconsistencias.empty:
            return "✅ ÉXITO: Los saldos de todos los almacenes coinciden con el consolidado mensual."
        else:
            num_errores = len(inconsistencias)
            return f"⚠️ ALERTA: Se encontraron inconsistencias en {num_errores} artículos. Revise el reporte de errores."