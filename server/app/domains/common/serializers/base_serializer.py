from abc import ABC, abstractmethod


class BaseSerializer(ABC):
    """Base class for domain serializers.

    Subclasses implement `to_json(**kwargs)` to convert a model instance to a JSON-safe dict.
    kwargs allow subclasses to accept optional serialization options (e.g. published_only).

    Usage:
        serializer = MySerializer(instance)
        data = serializer.to_json()
        data = serializer.to_json(published_only=True)
    """

    def __init__(self, instance):
        self.instance = instance

    @abstractmethod
    def to_json(self, **kwargs) -> dict:
        """Serialize the model instance to a JSON-safe dict."""
        ...
