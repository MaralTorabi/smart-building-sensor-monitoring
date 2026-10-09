"""Generic repository interface definition.

Provides the generic CRUD contract for all domain entity repositories.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, List, Optional, TypeVar

T = TypeVar("T")


class Repository(ABC, Generic[T]):
    """Abstract generic repository defining standard CRUD data access operations.

    Type parameter T represents the domain entity type managed by the repository.
    """

    @abstractmethod
    def add(self, entity: T) -> None:
        """Persists a new entity to the repository.

        Args:
            entity: Domain entity to add.
        """
        pass

    @abstractmethod
    def get_by_id(self, id: str) -> Optional[T]:
        """Retrieves an entity by its unique identifier.

        Args:
            id: Unique identifier string.

        Returns:
            The matching entity if found; None otherwise.
        """
        pass

    @abstractmethod
    def get_all(self) -> List[T]:
        """Retrieves all entities stored in this repository.

        Returns:
            A list containing all managed entities.
        """
        pass

    @abstractmethod
    def update(self, entity: T) -> bool:
        """Updates an existing entity in the repository.

        Args:
            entity: Domain entity with updated state.

        Returns:
            True if entity was found and updated; False otherwise.
        """
        pass

    @abstractmethod
    def delete(self, id: str) -> bool:
        """Deletes an entity from the repository by its identifier.

        Args:
            id: Identifier of the entity to delete.

        Returns:
            True if entity was found and removed; False otherwise.
        """
        pass
