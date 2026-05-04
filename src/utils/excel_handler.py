import pandas as pd
import os

class ExcelHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.data = {}

    def load_all_sheets(self):
        """Lee todas las hojas necesarias del Excel de entrada."""
        try:
            if not os.path.exists(self.file_path):
                return False, f"Error: No se encuentra el archivo en {self.file_path}"
            
            xls = pd.ExcelFile(self.file_path)
            required_sheets = ['ARTICULOS', 'ALMACENES', 'TIPOS_OPERACION', 'SALDOS_INICIALES', 'MOVIMIENTOS']
            
            for sheet in required_sheets:
                if sheet in xls.sheet_names:
                    # Cargamos la hoja y eliminamos espacios en blanco en los nombres de columnas
                    df = pd.read_excel(self.file_path, sheet_name=sheet)
                    df.columns = df.columns.str.strip()
                    self.data[sheet] = df
                else:
                    return False, f"Error: Falta la hoja obligatoria '{sheet}'"
            
            return True, "Carga de datos exitosa"
        except Exception as e:
            return False, f"Error al leer el Excel: {str(e)}"

    def save_reports(self, dataframes_dict, output_folder):
        """Guarda los reportes generados (Kardex, Inconsistencias) en la carpeta de reportes."""
        try:
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            for name, df in dataframes_dict.items():
                path = os.path.join(output_folder, f"{name}.xlsx")
                df.to_excel(path, index=False)
            return True, f"Reportes guardados en {output_folder}"
        except Exception as e:
            return False, f"Error al guardar reportes: {str(e)}"