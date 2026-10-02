# Guía de Configuración del Entorno de Desarrollo (Windows PowerShell)

## Prerrequisitos

- Python 3.11+ instalado.
- Permisos de ejecución de scripts habilitados en PowerShell.

## Pasos para Levantar el Ambiente

### 1. Habilitar ejecución de scripts (Solo una vez por máquina)

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

2. Crear el entorno virtual
   PowerShell
   py -m venv .venv
3. Activar el entorno virtual
   Windows (PowerShell): .\.venv\Scripts\Activate.ps1

Linux/macOS (Bash/Zsh): source .venv/bin/activate

4. Instalar dependencias
   PowerShell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
