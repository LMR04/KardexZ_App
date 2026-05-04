import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Importaciones internas
from src.utils.excel_handler import ExcelHandler
from src.logic.engine import KardexEngine
from src.logic.validator import InventoryValidator
from src.ui.journey_view import ProductJourneyView
from src.ui.components import InfoCard

class KardexApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Kardex-Z: Gestión de Inventarios Consolidado (Platanitos S.A.C.)")
        self.geometry("1150x750")
        
        self.handler = None
        self.engine = None
        self.df_detallado = None
        self.df_consolidado = None
        self.chart_canvas = None

        self._setup_ui()
        self._show_initial_logo()

    def _setup_ui(self):
        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        ctk.CTkLabel(self.sidebar, text="Kardex-Z v1.0", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=25)
        
        self.btn_load = ctk.CTkButton(self.sidebar, text="Cargar Base de Datos", command=self.load_data)
        self.btn_load.pack(pady=10, padx=20)
        
        self.btn_process = ctk.CTkButton(self.sidebar, text="Procesar Cierre", state="disabled", command=self.process_data)
        self.btn_process.pack(pady=10, padx=20)

        self.btn_export = ctk.CTkButton(self.sidebar, text="Exportar Reportes", state="disabled", fg_color="#28a745", hover_color="#218838", command=self.export_data)
        self.btn_export.pack(pady=10, padx=20)

        # Área Principal (Tabs)
        self.tabs = ctk.CTkTabview(self)
        self.tabs.pack(side="right", fill="both", expand=True, padx=20, pady=10)
        
        self.tab_resumen = self.tabs.add("Resumen Consolidado")
        self.tab_journey = self.tabs.add("Viaje del Producto")
        
        # Vista del Viaje
        self.journey_view = ProductJourneyView(self.tab_journey)
        self.journey_view.pack(fill="both", expand=True)
        self.journey_view.btn_search.configure(command=self.search_journey)

        # Contenedor de Resumen
        self.summary_container = ctk.CTkFrame(self.tab_resumen, fg_color="transparent")
        self.summary_container.pack(fill="both", expand=True)

        self.indicator_frame = ctk.CTkFrame(self.summary_container, fg_color="transparent")
        self.indicator_frame.pack(fill="x", pady=15)
        
        self.card_status = InfoCard(self.indicator_frame, "Estado de Validación", "Esperando carga de datos...")
        self.card_status.pack(side="top", padx=20, fill="x")

    def _show_initial_logo(self):
        """Muestra el logo de Platanitos centrado al inicio."""
        img_path = os.path.join(os.getcwd(), "src", "Platanitos.png")
        if os.path.exists(img_path):
            try:
                raw_img = Image.open(img_path)
                self.logo_img = ctk.CTkImage(light_image=raw_img, dark_image=raw_img, size=(600, 600))
                self.logo_label = ctk.CTkLabel(self.summary_container, image=self.logo_img, text="")
                self.logo_label.pack(pady=60)
            except Exception as e:
                print(f"No se pudo cargar la imagen: {e}")

    def load_data(self):
        path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if path:
            self.handler = ExcelHandler(path)
            success, msg = self.handler.load_all_sheets()
            if success:
                # Actualizar el ComboBox de SKUs automáticamente
                skus = sorted(self.handler.data['ARTICULOS']['Cod_Articulo'].unique().tolist())
                self.journey_view.update_sku_list(skus)
                
                self.btn_process.configure(state="normal")
                messagebox.showinfo("Éxito", "Base de datos cargada. Lista de productos actualizada.")
            else:
                messagebox.showerror("Error", msg)

    def process_data(self):
        try:
            # Procesamiento lógico
            self.engine = KardexEngine(self.handler.data)
            self.df_detallado = self.engine.process_kardex_detallado()
            self.df_consolidado = self.engine.process_kardex_consolidado()
            
            # Validación de integridad
            validator = InventoryValidator(self.df_detallado, self.df_consolidado)
            inconsistencias, _ = validator.check_inconsistencies()
            alert_msg = validator.get_summary_alerts(inconsistencias)
            
            # Actualizar Interfaz
            self.card_status.value_label.configure(text=alert_msg)
            if hasattr(self, 'logo_label'):
                self.logo_label.destroy()
            
            self._render_charts()
            self.btn_export.configure(state="normal")
            messagebox.showinfo("Proceso Completo", "Cierre mensual procesado correctamente.")
        except Exception as e:
            messagebox.showerror("Error de Cálculo", f"Hubo un problema procesando los datos: {str(e)}")

    def _render_charts(self):
        """Genera gráficos gerenciales sobre el valor del inventario."""
        if self.chart_canvas:
            self.chart_canvas.get_tk_widget().destroy()

        # Agregamos valor por almacén (última foto del mes)
        saldos_f = self.df_detallado.sort_values('Fecha').groupby(['Almacen', 'Articulo']).tail(1)
        resumen_valor = saldos_f.groupby('Almacen')['Saldo_Valor_Total'].sum()

        # Configuración de estilo Matplotlib para modo oscuro
        plt.rcParams.update({'text.color': "white", 'axes.labelcolor': "white", 'xtick.color': "white", 'ytick.color': "white"})
        fig, ax = plt.subplots(figsize=(6, 4), dpi=90)
        fig.patch.set_facecolor('#2b2b2b')
        ax.set_facecolor('#333333')

        resumen_valor.plot(kind='bar', ax=ax, color='#1f538d', edgecolor='white')
        ax.set_title("Valor Total de Inventario por Sede (S/.)", pad=15, fontsize=12, fontweight='bold')
        ax.set_xlabel("Almacén / Tienda")
        ax.set_ylabel("Soles (S/.)")
        plt.xticks(rotation=45)
        plt.tight_layout()

        self.chart_canvas = FigureCanvasTkAgg(fig, master=self.summary_container)
        self.chart_canvas.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=10)

    def search_journey(self):
        # Obtener SKU desde el ComboBox en lugar de un Entry manual[cite: 1]
        sku = self.journey_view.sku_combo.get().strip()
        if self.df_detallado is not None:
            df_sku = self.df_detallado[self.df_detallado['Articulo'] == sku].sort_values('Fecha')
            self.journey_view.render_journey(df_sku)

    def export_data(self):
        folder = filedialog.askdirectory()
        if folder:
            reports = {
                "Kardex_Por_Almacen": self.df_detallado,
                "Kardex_Consolidado": self.df_consolidado
            }
            success, msg = self.handler.save_reports(reports, folder)
            messagebox.showinfo("Exportación", msg)