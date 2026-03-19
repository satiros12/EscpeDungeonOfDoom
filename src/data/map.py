import json
from dataclasses import dataclass, field
from typing import Optional
from .entity import EntityDef, NPCDef, StaticDef, TorchDef, DoorDef


@dataclass
class MapData:
    name: str
    width: int
    height: int
    tiles: list[list[int]]
    entities: list[EntityDef] = field(default_factory=list)
    player_start: tuple[float, float, float] = (1.5, 5.0, 0.0)
    exit_door: Optional[DoorDef] = None
    is_final: bool = False

    def to_dict(self) -> dict:
        entities_list = []
        for e in self.entities:
            if isinstance(e, NPCDef):
                entities_list.append(
                    {
                        "type": e.type,
                        "x": e.x,
                        "y": e.y,
                        "patrol": e.patrol,
                        "health": e.health,
                    }
                )
            elif isinstance(e, StaticDef):
                entities_list.append(
                    {
                        "type": "static",
                        "sprite": e.sprite,
                        "x": e.x,
                        "y": e.y,
                        "animated": e.animated,
                    }
                )
            elif isinstance(e, TorchDef):
                entities_list.append(
                    {
                        "type": "torch",
                        "x": e.x,
                        "y": e.y,
                        "light_radius": e.light_radius,
                        "color": e.color,
                    }
                )

        result = {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "tiles": self.tiles,
            "entities": entities_list,
            "player_start": list(self.player_start),
            "is_final": self.is_final,
        }

        if self.exit_door:
            result["exit_door"] = {
                "x": self.exit_door.x,
                "y": self.exit_door.y,
                "next_map": self.exit_door.next_map,
            }

        return result

    def save(self, path: str):
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> "MapData":
        entities = []
        for e in data.get("entities", []):
            if e.get("type") == "static":
                entities.append(
                    StaticDef(
                        sprite=e["sprite"],
                        x=e["x"],
                        y=e["y"],
                        animated=e.get("animated", False),
                    )
                )
            elif e.get("type") == "torch":
                entities.append(
                    TorchDef(
                        x=e["x"],
                        y=e["y"],
                        light_radius=e.get("light_radius", 5.0),
                        color=e.get("color", "red"),
                    )
                )
            elif e.get("type") in ["soldier", "caco_demon", "cyber_demon"]:
                entities.append(
                    NPCDef(
                        type=e["type"],
                        x=e["x"],
                        y=e["y"],
                        patrol=e.get("patrol", []),
                        health=e.get("health", 100),
                    )
                )

        exit_door_data = data.get("exit_door")
        exit_door = None
        if exit_door_data:
            exit_door = DoorDef(
                x=exit_door_data["x"],
                y=exit_door_data["y"],
                next_map=exit_door_data.get("next_map"),
            )

        return cls(
            name=data["name"],
            width=data["width"],
            height=data["height"],
            tiles=data["tiles"],
            entities=entities,
            player_start=tuple(data.get("player_start", [1.5, 5.0, 0.0])),
            exit_door=exit_door,
            is_final=data.get("is_final", False),
        )

    @classmethod
    def load(cls, path: str) -> "MapData":
        with open(path, "r") as f:
            data = json.load(f)
        return cls.from_dict(data)
