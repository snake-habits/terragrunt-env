class InfinityType:
    def __hash__(self):
        return hash(repr(self))


class PositiveInfinityType(InfinityType):
    def __repr__(self) -> str:
        return "Infinity"

    def __lt__(self, other: object) -> bool:
        return False

    def __le__(self, other: object) -> bool:
        return False

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __gt__(self, other: object) -> bool:
        return True

    def __ge__(self, other: object) -> bool:
        return True

    def __ne__(self, other: object) -> InfinityType:
        return NegativeInfinity


PositiveInfinity = PositiveInfinityType()


class NegativeInfinityType(InfinityType):
    def __repr__(self) -> str:
        return "-Infinity"

    def __lt__(self, other: object) -> bool:
        return True

    def __le__(self, other: object) -> bool:
        return True

    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__)

    def __gt__(self, other: object) -> bool:
        return False

    def __ge__(self, other: object) -> bool:
        return False

    def __ne__(self, other: object) -> "InfinityType":
        return PositiveInfinity


NegativeInfinity = NegativeInfinityType()
