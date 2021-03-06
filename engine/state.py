"""A module for abstract state handling classes.

This module should have as few of its own dependencies as possible.
"""
from __future__ import annotations

import tcod

import g

MOVE_KEYS = {
    # Arrow keys.
    tcod.event.K_LEFT: (-1, 0),
    tcod.event.K_RIGHT: (1, 0),
    tcod.event.K_UP: (0, -1),
    tcod.event.K_DOWN: (0, 1),
    tcod.event.K_HOME: (-1, -1),
    tcod.event.K_END: (-1, 1),
    tcod.event.K_PAGEUP: (1, -1),
    tcod.event.K_PAGEDOWN: (1, 1),
    tcod.event.K_PERIOD: (0, 0),
    # Numpad keys.
    tcod.event.K_KP_1: (-1, 1),
    tcod.event.K_KP_2: (0, 1),
    tcod.event.K_KP_3: (1, 1),
    tcod.event.K_KP_4: (-1, 0),
    tcod.event.K_KP_5: (0, 0),
    tcod.event.K_CLEAR: (0, 0),
    tcod.event.K_KP_6: (1, 0),
    tcod.event.K_KP_7: (-1, -1),
    tcod.event.K_KP_8: (0, -1),
    tcod.event.K_KP_9: (1, -1),
    # Vi keys.
    tcod.event.K_h: (-1, 0),
    tcod.event.K_j: (0, 1),
    tcod.event.K_k: (0, -1),
    tcod.event.K_l: (1, 0),
    tcod.event.K_y: (-1, -1),
    tcod.event.K_u: (1, -1),
    tcod.event.K_b: (-1, 1),
    tcod.event.K_n: (1, 1),
}


class State(tcod.event.EventDispatch[None]):
    """An abstract state.  Subclasses should be made of this class to handle state."""

    def on_draw(self, console: tcod.console.Console) -> None:
        """Called when this state should be rendered.

        `console` will be cleared and drawn by the caller.
        """

    def cmd_cancel(self) -> None:
        """By default this will exit out of the current state."""
        assert g.states[-1] is self
        g.states.pop()

    def cmd_move(self, x: int, y: int) -> None:
        """Movement command.

        `x` and `y` are a direction which may also be `0,0`.
        """

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        """Dispatch keys to various commands.  This creates a consistant interface across states."""
        if event.sym == tcod.event.K_ESCAPE:
            self.cmd_cancel()
        elif event.sym in MOVE_KEYS:
            self.cmd_move(*MOVE_KEYS[event.sym])

    def ev_quit(self, event: tcod.event.Quit) -> None:
        """Exit the program a quickly as possible."""
        raise SystemExit()