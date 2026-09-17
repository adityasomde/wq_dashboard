from typing import Any

def resolve_choices(node: Any, settings: dict[str, Any]) -> list[dict[str, Any]] | None:
    if node is None:
        return None
    if isinstance(node, list):
        return [c for c in node if isinstance(c, dict)]
    if not isinstance(node, dict):
        return None

    for parent_field, branches in node.items():
        if not isinstance(branches, dict):
            continue
        chosen = settings.get(parent_field)
        if chosen is None:
            return None
        subtree = branches.get(chosen)
        if subtree is None:
            subtree = branches.get(str(chosen))
        if subtree is None:
            return None
        return resolve_choices(subtree, settings)
    return None

def dependencies(node: Any, found: list[str] | None = None) -> list[str]:
    found = found if found is not None else []
    if not isinstance(node, dict):
        return found
    for parent_field, branches in node.items():
        if not isinstance(branches, dict):
            continue
        found.append(parent_field)
        first = next(iter(branches.values()), None)
        return dependencies(first, found)
    return found

def resolve_options(schema: dict[str, Any], settings: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    settings = settings or {}
    resolved: dict[str, dict[str, Any]] = {}

    for name, node in schema.items():
        if not isinstance(node, dict):
            continue
        raw_choices = node.get("choices")
        choices = resolve_choices(raw_choices, settings)
        depends = dependencies(raw_choices)
        resolved[name] = {
            "name": name,
            "label": node.get("label", name),
            "type": node.get("type"),
            "required": bool(node.get("required", False)),
            "readOnly": bool(node.get("readOnly", False)),
            "choices": choices,
            "dependsOn": depends,
            "blocked": bool(depends) and choices is None,
            "min": node.get("min_value", node.get("minValue")),
            "max": node.get("max_value", node.get("maxValue")),
        }
    return resolved
