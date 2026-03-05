
class PricingBaseError(Exception):
    """Classe parente de toutes les erreurs métier."""
    pass


# ── Équipe Data Engineering (Jaddi / El Khelyfy) ───────────────────────────

class MarketUnreachableError(PricingBaseError):
    """
    Levée quand le scraper ne peut pas joindre la source de données
    (timeout réseau, blocage IP, site indisponible…).
    → HTTP 503 Service Unavailable
    """
    def __init__(self, source: str, reason: str = ""):
        self.source = source
        self.reason = reason
        super().__init__(f"Marché '{source}' inaccessible. {reason}".strip())


class InsufficientDataError(PricingBaseError):
    """
    Levée quand le scraper retourne trop peu de résultats pour être fiable
    (ex. moins de N annonces trouvées).
    → HTTP 404 Not Found
    """
    def __init__(self, product_name: str, found: int, minimum: int):
        self.product_name = product_name
        self.found = found
        self.minimum = minimum
        super().__init__(
            f"Données insuffisantes pour '{product_name}' : "
            f"{found} annonce(s) trouvée(s), minimum requis : {minimum}."
        )


# ── Équipe Data Science (Affoudji / Tafoughalti) ───────────────────────────

class StatisticsError(PricingBaseError):
    """
    Levée quand le calcul de statistiques échoue (données corrompues,
    valeurs aberrantes bloquantes, etc.).
    → HTTP 422 Unprocessable Entity
    """
    def __init__(self, detail: str = ""):
        super().__init__(f"Erreur lors du calcul des statistiques. {detail}".strip())


# ── Équipe IA (Boukechouch / El Yousfi) ────────────────────────────────────

class AIAgentError(PricingBaseError):
    """
    Levée quand l'Agent IA ne répond pas ou retourne un résultat invalide
    (clé API révoquée, réponse malformée, timeout LLM…).
    → HTTP 502 Bad Gateway
    """
    def __init__(self, detail: str = ""):
        super().__init__(f"L'agent IA n'a pas pu produire de conseil. {detail}".strip())


# ── Validation Pydantic / Contrat DTO ──────────────────────────────────────

class DataContractError(PricingBaseError):
    """
    Levée quand les données brutes ne respectent pas le contrat PricePoint.
    Utile pour le Contract Testing (Salma / Chaimaa).
    → HTTP 422 Unprocessable Entity
    """
    def __init__(self, detail: str = ""):
        super().__init__(f"Violation du contrat de données. {detail}".strip())
