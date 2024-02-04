"""The factory module for creating backends."""
from api.backends.base import BackendBase

class BackendFactory:
    """The factory class for creating backends."""
    registry = {}

    @classmethod
    def register(cls, name: str) -> callable:
        """Registers a backend class in the factory.

        Args:
        - name (str): The name of the backend.

        Returns:
        - callable: A decorator.
        """
        def decorator(backend_cls: BackendBase) -> BackendBase:
            cls.registry[name] = backend_cls
            return backend_cls
        return decorator

    @classmethod
    def create_backend(cls, backend_name: str) -> BackendBase:
        """Creates a backend instance."""
        backend_cls = cls.registry.get(backend_name)
        if backend_cls is None:
            raise TypeError(f"Backend {backend_name} not found. Registry: {cls.registry}")
        return backend_cls()
    