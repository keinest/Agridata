"""Utility script for local validation and Vercel deployment helpers."""
from pathlib import Path
import secrets
import subprocess
import sys


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
    print("AgriData Platform - Utilitaire local")
    print("=" * 64)
    print("1. Lancer le backend FastAPI")
    print("2. Servir le frontend statique")
    print("3. Initialiser la base MySQL")
    print("4. Valider le projet avant déploiement")
    print("5. Générer une SECRET_KEY")
    print("6. Déployer sur Vercel (CLI)")


def start_backend() -> None:
    run_command(
        ["python3", "-m", "uvicorn", "backend.app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        cwd=PROJECT_ROOT,
    )


def serve_frontend() -> None:
    run_command(["python3", "-m", "http.server", "3000"], cwd=PUBLIC_PATH)


def init_database() -> None:
    mysql_user = input("Utilisateur MySQL [root]: ").strip() or "root"
    mysql_host = input("Hôte MySQL [localhost]: ").strip() or "localhost"
    command = f"mysql -u {mysql_user} -p -h {mysql_host} < {BACKEND_PATH / 'database_init.sql'}"
    run_command(["bash", "-lc", command], cwd=PROJECT_ROOT)


def validate_project() -> None:
    checks = [
        (["python3", "-m", "compileall", "backend/app", "api"], PROJECT_ROOT),
        (["node", "--check", "public/assets/js/app.js"], PROJECT_ROOT),
        (["node", "--check", "public/assets/js/dashboard.js"], PROJECT_ROOT),
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
    run_command(["vercel"], cwd=PROJECT_ROOT)


def main() -> None:
    print_menu()
    choice = input("\nChoisissez une option [1-6]: ").strip()

    actions = {
        "1": start_backend,
        "2": serve_frontend,
        "3": init_database,
        "4": validate_project,
        "5": generate_secret_key,
        "6": deploy_vercel,
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
