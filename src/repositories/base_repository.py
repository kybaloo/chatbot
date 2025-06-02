"""
Module définissant les interfaces de base pour l'accès aux données
Implémente le pattern Repository pour abstraire la source de données
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar, Dict, Any

T = TypeVar('T')  # Type générique pour les entités


class BaseRepository(Generic[T], ABC):
    """
    Interface de base pour tous les repositories
    Définit les méthodes CRUD standard que tous les repositories doivent implémenter
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
    
    @abstractmethod
    async def find(self, filter_params: Dict[str, Any]) -> List[T]:
        """Recherche des entités selon des critères"""
        pass
