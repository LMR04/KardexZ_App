import subprocess
import os
import sys

def build_exe():
    app_name = "KardexZ_Platanitos"
    entry_point = os.path.join("src", "main.py")
    
    # Detectar el separador de rutas según el sistema operativo
    sep = ";" if sys.platform.startswith("win") else ":"
    
    # Incluir la imagen del logo en el paquete
    logo_path = os.path.join("src", "Platanitos.png")
    
    command = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--clean",
        f"--add-data=src{os.sep}Platanitos.png{sep}src", # Esto es la clave
        f"--name={app_name}",
        entry_point
    ]

    print(f"🚀 Iniciando empaquetado en sistema: {sys.platform}")
    try:
        subprocess.check_call(command)
        print(f"\n✅ ¡Éxito! El .exe está en la carpeta 'dist'")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    build_exe()