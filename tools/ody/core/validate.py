"""零依賴的最小 JSON Schema 驗證器。

只實作本框架用到的子集（required / type / enum / items / properties），
刻意不引入外部套件 jsonschema —— 呼應「省」：不裝、不連網、跨機免安裝。
"""
from __future__ import annotations

_PY_TYPES = {
    "object": dict,
    "array": list,
    "string": str,
    "integer": int,
    "number": (int, float),
    "boolean": bool,
}


class SchemaError(ValueError):
    pass


def validate(obj, schema, path: str = "$") -> None:
    """對 obj 套用 schema；不合即 raise SchemaError（訊息含路徑）。"""
    t = schema.get("type")
    if t:
        py = _PY_TYPES[t]
        # bool 是 int 子類，避免把 True 當 integer 放行
        if t in ("integer", "number") and isinstance(obj, bool):
            raise SchemaError(f"{path}: 期望 {t}，得到 boolean")
        if not isinstance(obj, py):
            raise SchemaError(f"{path}: 期望 {t}，得到 {type(obj).__name__}")

    if "enum" in schema and obj not in schema["enum"]:
        raise SchemaError(f"{path}: 值 {obj!r} 不在 enum {schema['enum']}")

    if schema.get("type") == "object":
        for key in schema.get("required", []):
            if key not in obj:
                raise SchemaError(f"{path}: 缺少必要欄位 '{key}'")
        props = schema.get("properties", {})
        for key, sub in props.items():
            if key in obj:
                validate(obj[key], sub, f"{path}.{key}")

    if schema.get("type") == "array" and "items" in schema:
        for i, item in enumerate(obj):
            validate(item, schema["items"], f"{path}[{i}]")
