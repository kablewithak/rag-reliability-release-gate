"""Explicit runtime component failures used by the deterministic thin slice."""


class ComponentConfigurationMismatchError(ValueError):
    """Raised before execution when a component does not match declared config."""


class RetrievalExecutionError(RuntimeError):
    """Raised when the retriever cannot complete its declared operation."""


class SourcePolicyExecutionError(RuntimeError):
    """Raised when source-policy filtering cannot complete."""


class ContextBudgetExhaustedError(RuntimeError):
    """Raised when no eligible evidence can fit the configured context budget."""


class ReplayResponseNotFoundError(RuntimeError):
    """Raised when the fake/replay provider has no response for a query."""


class CitationValidationExecutionError(RuntimeError):
    """Raised when citation validation cannot complete."""
