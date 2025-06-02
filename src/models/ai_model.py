"""
Modèle pour la configuration et l'interaction avec les modèles d'IA
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class AIModel:
    """Représente un modèle d'IA avec ses paramètres et capacités"""

    model_id: str  # Identifiant du modèle (ex: "mistral-small-latest")
    provider: str  # Fournisseur du modèle (ex: "mistral", "openai")
    name: str  # Nom lisible du modèle
    description: Optional[str] = None  # Description du modèle
    context_window: int = 4096  # Taille de la fenêtre de contexte en tokens
    max_tokens: int = 1024  # Nombre maximum de tokens en sortie
    supports_vision: bool = False  # Si le modèle supporte l'analyse d'images
    supports_audio: bool = False  # Si le modèle supporte l'analyse audio
    model_parameters: Dict[str, Any] = field(
        default_factory=dict
    )  # Paramètres spécifiques au modèle

    def to_dict(self):
        """Convertit le modèle en dictionnaire"""
        return {
            "model_id": self.model_id,
            "provider": self.provider,
            "name": self.name,
            "description": self.description,
            "context_window": self.context_window,
            "max_tokens": self.max_tokens,
            "supports_vision": self.supports_vision,
            "supports_audio": self.supports_audio,
            "model_parameters": self.model_parameters,
        }


# Modèles Mistral prédéfinis
MISTRAL_MODELS = {
    "mistral-tiny": AIModel(
        model_id="mistral-tiny",
        provider="mistral",
        name="Mistral Tiny",
        description="Modèle léger et rapide pour des tâches simples",
        context_window=4096,
        model_parameters={"temperature": 0.7, "top_p": 0.9},
    ),
    "mistral-small": AIModel(
        model_id="mistral-small-latest",
        provider="mistral",
        name="Mistral Small",
        description="Modèle polyvalent offrant un bon équilibre entre performance et qualité",
        context_window=8192,
        model_parameters={"temperature": 0.7, "top_p": 0.9},
    ),
    "mistral-medium": AIModel(
        model_id="mistral-medium-latest",
        provider="mistral",
        name="Mistral Medium",
        description="Modèle avancé pour des tâches complexes nécessitant une compréhension approfondie",
        context_window=32768,
        model_parameters={"temperature": 0.7, "top_p": 0.9},
    ),
    "mistral-large": AIModel(
        model_id="mistral-large-latest",
        provider="mistral",
        name="Mistral Large",
        description="Modèle le plus puissant de Mistral AI, idéal pour les tâches les plus exigeantes",
        context_window=32768,
        model_parameters={"temperature": 0.7, "top_p": 0.9},
    ),
}


def get_model_by_id(model_id: str) -> Optional[AIModel]:
    """Récupère un modèle par son ID"""
    return MISTRAL_MODELS.get(model_id)
