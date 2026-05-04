import customtkinter as ctk

class ProductJourneyView(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.grid_columnconfigure(0, weight=1)
        
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.sku_combo = ctk.CTkComboBox(search_frame, values=["Cargue datos primero..."], width=300)
        self.sku_combo.pack(side="left", padx=10)
        
        self.btn_search = ctk.CTkButton(search_frame, text="Rastrear", width=100)
        self.btn_search.pack(side="left", padx=10)

        self.timeline_frame = ctk.CTkScrollableFrame(self, label_text="Cronología de Movimientos")
        self.timeline_frame.pack(fill="both", expand=True, padx=20, pady=10)

    def update_sku_list(self, sku_list):
        self.sku_combo.configure(values=sku_list)
        self.sku_combo.set(sku_list[0])

    # AGREGAR ESTA FUNCIÓN QUE FALTABA
    def render_journey(self, df_kardex_sku):
        """Dibuja visualmente el camino del producto."""
        for widget in self.timeline_frame.winfo_children():
            widget.destroy()

        if df_kardex_sku.empty:
            ctk.CTkLabel(self.timeline_frame, text="No se encontraron movimientos.").pack(pady=20)
            return

        for idx, row in df_kardex_sku.iterrows():
            item_frame = ctk.CTkFrame(self.timeline_frame, border_width=1)
            item_frame.pack(fill="x", pady=5, padx=5)
            
            # Traducción de códigos para el profesor
            tipo_txt = "Transferencia" if str(row['Tipo_Op']) == "11" else "Compra" if str(row['Tipo_Op']) == "02" else "Venta"
            
            info = f"📅 {row['Fecha'].strftime('%d/%m/%Y %H:%M')} | 📍 {row['Almacen']}\n"
            info += f"Operación: {tipo_txt} | Cant: {row['Cant']} | Saldo Local: {row['Saldo_Cant']}"
            
            ctk.CTkLabel(item_frame, text=info, justify="left", anchor="w").pack(padx=10, pady=10, fill="x")
            
            if idx < df_kardex_sku.index[-1]:
                ctk.CTkLabel(self.timeline_frame, text="↓", font=ctk.CTkFont(size=20)).pack()