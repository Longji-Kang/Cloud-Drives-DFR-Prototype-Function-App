from enum import Enum

# Enums for action types
class ACTION_TYPE(Enum):
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"

# Enums for types of modification
class MODIFICATION_TYPE(Enum):
    CONTENT_MODIFICATION = "content modification"
    RENAME               = "rename modification"
    REPLACE              = "replace modification"