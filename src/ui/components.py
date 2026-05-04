import customtkinter as ctk

class InfoCard(ctk.CTkFrame):
    """Tarjeta para mostrar indicadores rápidos (Stock Total, Alertas)."""
    def __init__(self, master, title, value, color="transparent"):
        super().__init__(master, fg_color=color, corner_radius=10, border_width=1)
        
        self.title_label = ctk.CTkLabel(self, text=title, font=ctk.CTkFont(size=12, weight="bold"))
        self.title_label.pack(pady=(10, 0), padx=15)
        
        self.value_label = ctk.CTkLabel(self, text=value, font=ctk.CTkFont(size=20, weight="bold"))
        self.value_label.pack(pady=(5, 10), padx=15)

class DataTable(ctk.CTkScrollableFrame):
    """Contenedor simple para mostrar datos tipo tabla."""
    def __init__(self, master, headers, **kwargs):
        super().__init__(master, **kwargs)
        self.headers = headers
        self._setup_headers()

    def _setup_headers(self):
        for i, header in enumerate(self.headers):
            lbl = ctk.CTkLabel(self, text=header, font=ctk.CTkFont(weight="bold"), anchor="w")
            lbl.grid(row=0, column=i, padx=10, pady=5, sticky="nsew")

    def update_data(self, df_rows):
        # Limpiar filas anteriores (excepto headers)
        for widget in self.winfo_children():
            if int(widget.grid_info()["row"]) > 0:
                widget.destroy()
        
        # Insertar nuevas filas
        for r_idx, row in enumerate(df_rows):
            for c_idx, value in enumerate(row):
                lbl = ctk.CTkLabel(self, text=str(value), anchor="w")
                lbl.grid(row=r_idx + 1, column=c_idx, padx=10, pady=2, sticky="nsew")