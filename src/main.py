import customtkinter as ctk
from src.ui.app_gui import KardexApp

def main():
    # Configuración del tema visual
    ctk.set_appearance_mode("System")  # "System", "Dark", or "Light"
    ctk.set_default_color_theme("blue")  # Tema de color principal

    # Instanciación y ejecución de la aplicación
    app = KardexApp()
    
    # Manejo de cierre seguro
    app.protocol("WM_DELETE_WINDOW", app.quit)
    
    app.mainloop()

if __name__ == "__main__":
    main()