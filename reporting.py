import os
import datetime
import logging

logger = logging.getLogger(__name__)

# FIX: chemin configurable via variable d'environnement avec fallback sur /tmp.
# Écrire dans le répertoire courant est risqué dans un conteneur Docker
# (répertoire éphémère, permissions variables selon l'image de base).
REPORT_DIR = os.getenv("REPORT_DIR", "/tmp")


def generate_system_report() -> str:
    """
    Génère un rapport de santé des services et le persiste sur disque.

    Returns:
        Le chemin absolu du fichier rapport généré.
    """
    logger.info("Démarrage du scan des services...")

    # Simulation de la vérification (en situation réelle, requêtes HTTP vers chaque service)
    services = {
        "Team 1 (Price)": "OPÉRATIONNEL",
        "Team 2 (Data)": "OPÉRATIONNEL",
        "Team 3 (Engine)": "INDISPONIBLE (Timeout)",
    }

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "==========================================",
        "RAPPORT DE SANTÉ DE L'ORCHESTRATEUR",
        f"Généré le : {timestamp}",
        "==========================================",
        "",
        "STATUT DES SERVICES :",
        "--------------------",
    ]

    for name, service_status in services.items():
        lines.append(f"- {name} : {service_status}")

    lines += [
        "",
        "INFOS SYSTÈME :",
        f"- App Name: {os.getenv('APP_NAME', 'Orchestrator')}",
        "- Environnement: Docker Container",
    ]

    report_content = "\n".join(lines)
    report_path = os.path.join(REPORT_DIR, "health_report.txt")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    logger.info("Rapport '%s' généré avec succès.", report_path)
    return report_path


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generate_system_report()
