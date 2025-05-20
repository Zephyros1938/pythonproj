from dataclasses import dataclass

@dataclass(frozen=True)
class GameTime:
    """Immutable snapshot passed to update/draw logic."""
    delta:   float   # Seconds since previous frame
    total:   float   # Seconds since the start of the program

class Time:
    """
    High‑resolution timer that produces a GameTime each frame.
    Call Time.tick() exactly once per frame.
    """
    def __init__(self, _clock):
        self._clock      = _clock
        self._start      = self._clock()
        self._last       = self._start
        self.delta       = 0.0
        self.total       = 0.0

    def tick(self) -> GameTime:
        now             = self._clock()
        self.delta       = now - self._last
        self.total       = now - self._start
        self._last       = now
        return GameTime(self.delta, self.total)
