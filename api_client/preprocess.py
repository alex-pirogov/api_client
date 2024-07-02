from typing import Any, Callable, TypeVar

from pydantic.alias_generators import to_camel, to_pascal, to_snake

T = TypeVar('T', dict[str, Any], list[dict[str, Any]])


def transform_keys(data: T, func: Callable[[str], str]) -> T:
    if type(data) is list:
        return [transform_keys(el, func) for el in data]

    if type(data) is not dict:
        return data

    return {func(k): transform_keys(v, func) for k, v in data.items()}


def dict_to_lower_keys(data: T) -> T:
    return transform_keys(data, lambda k: k.lower())


def dict_to_snake_keys(data: T) -> T:
    return transform_keys(data, lambda k: to_snake(k))


def dict_to_pascal_keys(data: T) -> T:
    return transform_keys(data, lambda k: to_pascal(k))


def dict_to_camel_keys(data: T) -> T:
    return transform_keys(data, lambda k: to_camel(k))
