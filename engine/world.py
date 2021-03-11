"""World class module."""
from __future__ import annotations

import logging
import random
from typing import List, Optional

import engine.actor
import engine.map
import engine.spells

logger = logging.getLogger(__name__)


class World:
    """This class is used to hold everything you'll want to save between sessions."""

    map: engine.map.Map

    def __init__(self) -> None:
        self.rng = random.Random()
        self.spell_slots: List[Optional[engine.spells.Spell]] = [
            engine.spells.PlaceActor(name="Place bomb", cooldown=8, spawn=engine.actor.Bomb),
            engine.spells.Beam(name="Ice beam", cooldown=3, effect=engine.effects.Cold(power=2)),
            engine.spells.Beam(name="Heat beam", cooldown=8, effect=engine.effects.Heat(power=5)),
            engine.spells.PlaceActor(name="Place totem", cooldown=8, spawn=engine.actor.Totem),
            engine.spells.Blast(name="Heat blast", cooldown=8, effect=engine.effects.Heat(), range=5),
            engine.spells.PlaceActor(name="Seeking bomb", cooldown=12, spawn=engine.actor.FlyingBomb),
            None,
            None,
            engine.spells.EarthVision(name="Earth Vision", cooldown=24, length=12),
            None,
        ]  # Spells equipped to the hotbar.
        assert len(self.spell_slots) == 10
        self.log: List[str] = []  # Text log.
        self.player = engine.actor.Player(0, 0)

    def report(self, message: str) -> None:
        """Append to the text log."""
        logger.info(message)
        self.log.append(message)

    def loop(self) -> None:
        while self.player in self.map.actors:
            next_obj = self.map.schedule[0]
            if next_obj is self.player:
                self.map.reveal(self.player.get_fov())  # Player remembers visible tiles.
            if next_obj.skip_turns == 0:
                try:
                    next_obj.on_turn()
                except engine.actions.StopAction as exc:
                    if self.player is next_obj:
                        self.report(exc.args[0])
                        continue  # Start over and call next_obj.on_turn again.
            else:
                next_obj.skip_turns -= 1
            if self.map.schedule and self.map.schedule[0] is next_obj:
                self.map.schedule.rotate(1)
                # All end-of-turn effects.
                if isinstance(next_obj, engine.actor.Actor):
                    next_obj.on_end_turn()
                if next_obj is self.player:
                    # End of player's turn.
                    for spell in self.spell_slots:
                        if spell is None:
                            continue
                        if spell.cooldown_left:
                            spell.cooldown_left -= 1
        logger.info("Player is dead or missing!")
