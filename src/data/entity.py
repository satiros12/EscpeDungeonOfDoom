from dataclasses import dataclass, field
from typing import Union, Optional


@dataclass
class NPCDef:
    type: str
    x: float
    y: float
    patrol: list[tuple[float, float]] = field(default_factory=list)
    health: int = 100


@dataclass
class StaticDef:
    sprite: str
    x: float
    y: float
    animated: bool = False


@dataclass
class TorchDef:
    x: float
    y: float
    light_radius: float = 5.0
    color: str = "red"


@dataclass
class DoorDef:
    x: float
    y: float
    next_map: Optional[str] = None


EntityDef = Union[NPCDef, StaticDef, TorchDef, DoorDef]

NPC_TYPES = ["soldier", "caco_demon", "cyber_demon"]

STATIC_SPRITES = ["candlebra", "barrel", "column"]

TORCH_COLORS = ["red", "green"]
