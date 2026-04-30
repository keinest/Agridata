"""Utility script for local validation and Vercel deployment helpers."""
import secrets
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
BACKEND_PATH = PROJECT_ROOT / "backend"
PUBLIC_PATH = PROJECT_ROOT / "public"


def run_command(cmd: list[str], cwd: Path | None = None) -> bool:
    """Run a command and stream output to the terminal."""
    print(f"\n$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd or PROJECT_ROOT, check=False)
    return result.returncode == 0


def print_menu() -> None:
    print("=" * 64)
    print("AgriData Platform (Flask) — Utilitaire local")
    print("=" * 64)
    print("1. Lancer le backend Flask (mode dev)")
    print("2. Lancer le backend Flask (gunicorn)")
    print("3. Servir le frontend statique")
    print("4. Initialiser la base JSON")
    print("5. Valider le projet avant déploiement")
    print("6. Générer une SECRET_KEY")
    print("7. Déployer sur Vercel (CLI)")


def start_backend_dev() -> None:
    run_command(
        [
            "python3", "-m", "flask",
            "--app", "backend.app.main:app",
            "run",
            "--reload",
            "--host", "0.0.0.0",
            "--port", "8000",
        ],
        cwd=PROJECT_ROOT,
    )


def start_backend_prod() -> None:
    run_command(
        [
            "gunicorn",
            "backend.app.main:app",
            "--bind", "0.0.0.0:8000",
            "--workers", "4",
            "--timeout", "120",
        ],
        cwd=PROJECT_ROOT,
    )


def serve_frontend() -> None:
    run_command(["python3", "-m", "http.server", "3000"], cwd=PUBLIC_PATH)


def init_database() -> None:
    print("JSON database initialization — no action needed.")
    print("Data files will be created automatically in the data/ directory.")


def validate_project() -> None:
    checks = [
        (["python3", "-m", "compileall", "backend/app", "api"], PROJECT_ROOT),
    ]
    failed = False
    for cmd, cwd in checks:
        ok = run_command(cmd, cwd=cwd)
        failed = failed or not ok

    if failed:
        print("\nValidation terminée avec erreurs.")
        sys.exit(1)

    print("\nValidation terminée avec succès.")


def generate_secret_key() -> None:
    secret_key = secrets.token_urlsafe(48)
    print("\nAjoutez cette valeur dans vos variables d'environnement :")
    print(f"SECRET_KEY={secret_key}")


def deploy_vercel() -> None:
    print("\nAssurez-vous d'avoir déjà configuré les variables d'environnement dans Vercel.")
    run_command(["vercel", "--prod"], cwd=PROJECT_ROOT)


def main() -> None:
    print_menu()
    choice = input("\nChoisissez une option [1-7]: ").strip()

    actions = {
        "1": start_backend_dev,
        "2": start_backend_prod,
        "3": serve_frontend,
        "4": init_database,
        "5": validate_project,
        "6": generate_secret_key,
        "7": deploy_vercel,
    }

    action = actions.get(choice)
    if action is None:
        print("Option invalide.")
        sys.exit(1)

    action()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nArrêt demandé.")
        sys.exit(0)
