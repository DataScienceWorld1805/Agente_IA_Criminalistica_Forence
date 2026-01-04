"""
Script para ejecutar la interfaz Gradio del sistema RAG criminológico.
"""
import argparse
import sys
from ui.gradio_app import launch_app


def main():
    """Función principal para ejecutar la interfaz Gradio."""
    parser = argparse.ArgumentParser(
        description="Lanza la interfaz web Gradio para el sistema RAG criminológico"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Dirección del servidor (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Puerto del servidor (default: 7860)"
    )
    parser.add_argument(
        "--share",
        action="store_true",
        help="Crear un enlace público compartido (Gradio Share)"
    )
    
    args = parser.parse_args()
    
    try:
        print("="*60)
        print("SISTEMA RAG CRIMINOLÓGICO - Interfaz Gradio")
        print("="*60)
        print(f"\nIniciando servidor en http://{args.host}:{args.port}")
        if args.share:
            print("Enlace público compartido habilitado")
        print("\nPresiona Ctrl+C para detener el servidor")
        print("="*60 + "\n")
        
        launch_app(
            server_name=args.host,
            server_port=args.port,
            share=args.share
        )
    except KeyboardInterrupt:
        print("\n\nServidor detenido por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError al iniciar el servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
