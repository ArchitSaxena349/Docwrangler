# Compatibility shim: re-export models from core.models
from core.models import *

# Define __all__ for clarity
from core.models import __all__ as _core_all
__all__ = list(_core_all)
