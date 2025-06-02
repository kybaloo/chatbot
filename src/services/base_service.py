"""
Base de services pour l'application
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Dict, Any

T = TypeVar("T")  # Type générique pour les entités


class BaseService(Generic[T], ABC):
    """
    Classe de base pour tous les services
    Définit les méthodes standard que tous les services doivent implémenter
    """

    @abstractmethod
    async def get(self, id: str) -> Optional[T]:
        """Récupère une entité par son ID"""
        pass

    @abstractmethod
    async def get_all(self) -> List[T]:
        """Récupère toutes les entités"""
        pass

    @abstractmethod
    async def create(self, entity: T) -> T:
        """Crée une nouvelle entité"""
        pass

    @abstractmethod
    async def update(self, id: str, entity: T) -> Optional[T]:
        """Met à jour une entité existante"""
        pass

    @abstractmethod
    async def delete(self, id: str) -> bool:
        """Supprime une entité par son ID"""
        pass
