from dataclasses import dataclass

@dataclass(init=False, frozen=True)
class MATH:
    PI = 3.141592
    TAU = PI * 2
    HALF_PI = PI / 2
    THIRD_PI = PI / 3
    TWO_THIRD_PI = THIRD_PI * 2
