"""Application exceptions."""


class IngestionError(Exception):
  """Raised when live marketplace data cannot be collected."""

  def __init__(self, message: str):
    self.message = message
    super().__init__(message)
