"""Actor class module"""
from __future__ import annotations

import logging
from typing import Optional, Tuple, Type

import numpy as np
import tcod

import engine.actions
import engine.map
import engine.states
import g
from engine.sched import Schedulable

logger = logging.getLogger(__name__)


class Actor(Schedulable):
    """Objects which are able to move on their own."""

    ch = "X"
    fg = (0xFF, 0xFF, 0xFF)
    default_ai: Type[engine.actions.Action] = engine.actions.DefaultAI
    faction = "hostile"

    def __init__(
        self, x: int, y: int, *, ai: Optional[Type[engine.actions.Action]] = None, faction: Optional[str] = None
    ):
        self.x = x
        self.y = y
        self.hp = 10
        self.ai = ai(self) if ai is not None else self.default_ai(self)
        if faction is not None:
            self.faction = faction

    def on_turn(self) -> None:
        assert self.ai.actor is self
        self.ai.perform()

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        """Take damage or trigger side-effects."""
        damage = effect.power  # Placeholder.
        g.world.report(f"{self} takes {damage} damage.")
        self.hp -= damage
        if self.hp <= 0:
            g.world.report(f"{self} dies.")
            g.world.map.remove_actor(self)

    @property
    def xy(self) -> Tuple[int, int]:
        """This actors current position."""
        return self.x, self.y

    def get_fov(self) -> np.ndarray:
        """Return a bool array of tiles this actor can see."""
        return tcod.map.compute_fov(
            transparency=g.world.map.tiles["transparent"], pov=self.xy, algorithm=tcod.FOV_SYMMETRIC_SHADOWCAST
        )


class Player(Actor):
    default_ai = engine.actions.PlayerControl
    ch = "@"
    faction = "player"


class Bomb(Actor):
    """Counts down to zero and then deletes nearby actors."""

    faction = "player"
    default_ai: Type[engine.actions.Action] = engine.actions.IdleAction

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.timer = 5
        self.ch = str(self.timer)

    def explode(self) -> None:
        # Should be replaced by an effect.
        for actor in list(g.world.map.actors):
            dist = abs(actor.x - self.x) + abs(actor.y - self.y)
            if dist <= 2:
                g.world.map.remove_actor(actor)

    def on_turn(self) -> None:
        super().on_turn()
        self.timer -= 1
        if self.timer < 0:
            self.explode()
        else:
            self.ch = str(self.timer)

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        """Explodes immediately if hit with a heat attacks."""
        if isinstance(effect, engine.effects.Heat):
            self.explode()


class Totem(Actor):
    default_ai: Type[engine.actions.Action] = engine.actions.IdleAction
    faction = "player"

    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.ch = "&"

    def apply_effect(self, effect: engine.effects.Effect) -> None:
        g.world.map.remove_actor(self)
        for y in range(self.y - 2, self.y + 3):
            for x in range(self.x - 2, self.x + 3):
                effect.apply(x, y)


class FlyingBomb(Bomb):
    faction = "player"
    default_ai: Type[engine.actions.Action] = engine.actions.SeekEnemy

class HunterEnemy(Actor):
    faction = "hostile"
    default_ai: Type[engine.actions.Action] = engine.actions.SeekEnemy
    #does two damage
    def attack(self) -> None:
        # Should be replaced by an effect.
        for actor in list(g.world.map.actors):
            dist = abs(actor.x - self.x) + abs(actor.y - self.y)
            if dist <= 1:
                if actor.faction != self.faction:
                    actor.hp = actor.hp - 2

    def on_turn(self) -> None:
        super().on_turn()
