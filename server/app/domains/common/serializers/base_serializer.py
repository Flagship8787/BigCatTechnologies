from abc import ABC, abstractmethod


class BaseSerializer(ABC):
    """Base class for domain serializers.

    Subclasses implement `to_json()` to convert a model instance to a JSON-safe dict.

    Usage:
        serializer = MySerializer(instance)
        data = serializer.to_json()
    """

    def __init__(self, instance):
        self.instance = instance

    @abstractmethod
    def to_json(self) -> dict:
        """Serialize the model instance to a JSON-safe dict."""
        ...
