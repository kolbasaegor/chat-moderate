from abc import abstractmethod
from typing import TypeVar, List, NewType


class Match:
    @abstractmethod
    def matches(self, *args, **kwargs) -> bool:
        # Use kwargs in order to extend the behaviour of this method
        pass


MatchType = NewType('Match', Match)


class All(Match):
    def __init__(self, *rules: MatchType):
        self._rules = rules

    def matches(self, *args, **kwargs) -> bool:
        for arg in args:
            for rule in self._rules:
                if not rule.matches(arg, **kwargs):
                    return False

        return True


class Any(Match):
    def __init__(self, *rules: MatchType):
        self._rules = rules

    def matches(self, *args, **kwargs) -> bool:
        for arg in args:
            for rule in self._rules:
                if rule.matches(arg, **kwargs):
                    return True

        return False


class Not(Match):
    def __init__(self, *rules: MatchType):
        self._rules = rules

    def matches(self, *args, **kwargs):
        for arg in args:
            for rule in self._rules:
                if rule.matches(arg, **kwargs):
                    return False

        return True
