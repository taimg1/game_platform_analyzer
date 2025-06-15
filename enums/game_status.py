from enum import Enum


class GameStatusEnum(str, Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    COMING_SOON = "coming_soon"
    PREORDER = "preorder"
    FREE = "free"
    UNAVAILABLE = "unavailable"
    EARLY_ACCESS = "early_access"
    BETA = "beta"
    REGION_LOCKED = "region_locked"
    UNKNOWN = "unknown"
