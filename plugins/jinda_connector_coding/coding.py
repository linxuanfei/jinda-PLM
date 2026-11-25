"""Connector part numbers from 津达电子连接器产品料号编码原则 B05 (2026-08-03).

The part number is one global string. Old numbers stay as they are. A new
number is refused when that string already exists, whether or not the
existing value follows B05.

Confirmed corrections to the PDF:
- 有卤 / 无卤 (the PDF text extraction can show 囟).
- Position ⑤ for 卡钩: A is 左卡钩, B is 右卡钩.
- 通用型 is the letter O.
- 特殊代码 has no fixed list. It is kept as written.
- 流水 is not zero-padded. ``1``, ``01`` and ``15`` are different spellings.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping

CATEGORIES = {
    "T": "压接式",
    "F": "FPC",
    "Y": "Type C",
    "A": "汽车",
    "E": "储能",
    "H": "高频高速",
    "C": "通讯",
    "N": "网络接口",
    "B": "板对板",
}

TYPES = {
    "Y": "胶壳",
    "W": "针座",
    "B": "胶芯",
    "C": "盖子",
    "T": "端子",
    "S": "铁壳",
    "K": "卡钩",
    "P": "端子PIN",
    "M": "锁扣",
    "D": "拉扣",
    "U": "套子",
    "N": "Insert molding",
}

# 2.1.1, also used by 针座, 胶芯, 盖子, 拉扣, 套子, Insert.
HOUSING_FORMS = {
    "O": "通用型",
    "L": "立贴",
    "R": "卧贴",
    "S": "上接",
    "H": "立式过板",
    "J": "卧式过板",
    "N": "加装铁壳",
    "X": "下接",
    "G": "公端（空中对插）",
    "M": "母端（空中对插）",
    "C": "夹板式公端",
}

# 2.5.1 端子. L/R here are 立式/卧式, not the housing 立贴/卧贴.
TERMINAL_FORMS = {
    "O": "通用型",
    "L": "立式",
    "R": "卧式",
    "D": "低脚",
    "I": "高脚",
    "X": "斜脚",
    "G": "公端（空中对插）",
    "M": "母端（空中对插）",
}

# 2.8.1 端子 PIN and 锁扣.
PIN_FORMS = {
    "O": "通用型",
    "L": "立贴",
    "R": "卧贴",
    "H": "立式过板",
    "J": "卧式过板",
    "S": "上接",
    "X": "下接",
    "Z": "直针",
    "W": "弯针",
}

SHELL_FORMS = {"": "上下通用", "A": "上铁壳", "B": "下铁壳"}
# PDF prints B as 左卡钩 as well. A is left and B is right.
HOOK_FORMS = {"": "左右通用", "A": "左卡钩", "B": "右卡钩"}
LOCK_SIDES = {"": "左右通用", "A": "左锁扣", "B": "右锁扣"}

PLASTIC_MATERIALS = {
    "1": "PA66有卤",
    "2": "PA66无卤",
    "3": "PA46",
    "4": "PA9T",
    "5": "PA6T有卤",
    "6": "PA6T无卤",
    "7": "PBT",
    "8": "LCP",
    "9": "PA66灼热丝",
    "0": "其他（PA10T）",
}

METAL_MATERIALS = {
    "1": "黄铜（青铜）",
    "2": "磷铜（磷青铜）",
    "3": "不锈钢",
    "4": "铍铜",
    "5": "高导铜",
}

COLORS = {
    "A": "白色",
    "B": "黑色",
    "C": "红色",
    "D": "黄色",
    "E": "蓝色",
    "F": "灰色",
    "G": "米色",
    "H": "青色",
    "I": "紫色",
    "J": "花白色",
}

PACKAGING = {"A": "卷装（载带）", "B": "管装", "C": "盒装"}
CAPS = {"1": "加盖子", "2": "贴麦拉"}

PLASTIC_TYPES = frozenset("YWBCDUN")
METAL_TYPES = frozenset("TSKPM")
PIN_COUNT_TYPES = frozenset("YWBDUNS")
COLOR_TYPES = frozenset("YWBCDUN")
PLATING_TYPES = frozenset("TPM")
SIDE_TYPES = frozenset("PM")

_B05_PREFIX = re.compile(r"^(?:000|\d+\.\d+)[A-Z]-(?:\d+|[A-Z]+)-[A-Z]")
_PLATING = re.compile(r"^([AB])(0|1|2|3[A-Z]?|4[A-Z]?)$")
_PINS = re.compile(r"^(?:([12])x)?(\d+)P([A-Z])?$")


class CodingError(ValueError):
    """The string or the fields break B05."""

    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(message)


class DuplicatePartNumber(ValueError):
    """The part number is already in the global pool."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(f"Part number already exists: {code}")


def canonicalize(code: str) -> str:
    """Uppercase codes and keep the row mark as a lowercase x, as in ``2x5P``."""
    text = str(code).strip()
    chars = []
    for index, char in enumerate(text):
        if char in "xX" and _is_row_mark(text, index):
            chars.append("x")
        else:
            chars.append(char.upper())
    return "".join(chars)


def looks_like_b05(code: str) -> bool:
    """True when the string has a B05 pitch, category, serial and type slot."""
    return _B05_PREFIX.match(canonicalize(code)) is not None


def format_pitch(value) -> str:
    text = str(value).strip()
    if text == "000":
        return "000"
    if not re.fullmatch(r"\d+(?:\.\d+)?", text):
        raise CodingError("pitch", "Pitch must be 000 or a decimal such as 0.5, 1.0, 1.25")
    whole, frac = (text.split(".", 1) + ["0"])[:2]
    frac = frac.rstrip("0") or "0"
    if int(whole) == 0 and set(frac) <= {"0"}:
        raise CodingError("pitch", "Pitch must be 000 or a positive decimal")
    return f"{int(whole)}.{frac}"


def format_serial(value) -> str:
    """Keep the given digits or letters. Do not add or remove zeros."""
    text = str(value).strip().upper()
    if not re.fullmatch(r"\d+|[A-Z]+", text):
        raise CodingError("serial", "Serial must be digits or letters")
    return text


def next_serial(category: str, used: Iterable[str] = ()) -> str:
    """Next 流水 for a category. Supplied serials are not rewritten by this.

    T uses 1, 2, 3. F uses A, B, C. Other categories use 1, 2, 3. Letters for
    those categories are accepted when supplied; the standard does not say
    when the digits are exhausted.
    """
    code = str(category).strip().upper()
    if code not in CATEGORIES:
        raise CodingError("category", f"Illegal category code {code}")
    taken = {format_serial(item) for item in used}
    if code == "F":
        number = 1
        while True:
            serial = _letters(number)
            if serial not in taken:
                return serial
            number += 1
    number = 1
    while True:
        serial = str(number)
        if serial not in taken:
            return serial
        number += 1


def generate(fields: Mapping) -> str:
    """Build one B05 part number. ``serial`` is copied, not padded."""
    data = _normalize(fields)
    _check(data)
    return _render(data)


def validate(code: str) -> dict:
    """Parse a B05 part number. Raise CodingError when a code is illegal."""
    text = canonicalize(code)
    if not looks_like_b05(text):
        raise CodingError("code", "Not a B05 part number")
    data = _parse(text)
    _check(data)
    rendered = _render(data)
    if rendered != text:
        raise CodingError("code", "Part number does not match B05")
    return data


def create_part_number(fields: Mapping, existing: Iterable[str]) -> str:
    """Generate a B05 number and refuse it when the pool already has it."""
    code = generate(fields)
    assert_available(code, existing)
    return code


def import_part_number(code: str, existing: Iterable[str]) -> str:
    """Accept a legacy number, or a valid B05 number, unless it already exists."""
    text = str(code).strip()
    if text == "":
        raise CodingError("code", "Empty part number")
    if looks_like_b05(text):
        text = generate(validate(text))
    assert_available(text, existing)
    return text


def screen_ipn(ipn, matches: Iterable[str]) -> str | None:
    """Check one IPN against B05 (when it looks like B05) and against matches.

    ``matches`` must be other part numbers only, not this part's own IPN.
    A blank IPN is left alone. Legacy numbers are not rewritten.
    """
    if ipn is None:
        return None
    text = str(ipn).strip()
    if text == "":
        return None
    if looks_like_b05(text):
        text = generate(validate(text))
    assert_available(text, matches)
    return text


def assert_available(code: str, existing: Iterable[str]) -> None:
    folded = str(code).strip().casefold()
    if folded == "":
        raise CodingError("code", "Empty part number")
    for item in existing:
        if item is None:
            continue
        other = str(item).strip()
        if other and other.casefold() == folded:
            raise DuplicatePartNumber(str(code).strip())


def _normalize(fields: Mapping) -> dict:
    data = {
        "pitch": format_pitch(fields.get("pitch", "")),
        "category": _token(fields.get("category", "")),
        "serial": format_serial(fields.get("serial", "")),
        "type": _token(fields.get("type", "")),
        "form": _token(fields.get("form", "")),
        "material": _token(fields.get("material", "")),
        "rows": _token(fields.get("rows", "")),
        "pins": _pins(fields.get("pins", "")),
        "color": _token(fields.get("color", "")),
        "special": _special(fields.get("special", "")),
        "packaging": _token(fields.get("packaging", "")),
        "cap": _token(fields.get("cap", "")),
        "plating_process": _token(fields.get("plating_process", "")),
        "plating": _token(fields.get("plating", "")),
        "side": _token(fields.get("side", "")),
    }
    return data


def _check(data: dict) -> None:
    if data["category"] not in CATEGORIES:
        raise CodingError("category", f"Illegal category code {data['category']}")
    if data["type"] not in TYPES:
        raise CodingError("type", f"Illegal type code {data['type']}")
    kind = data["type"]
    forms = _forms(kind)
    if data["form"] not in forms:
        raise CodingError("form", f"Illegal form code {data['form'] or '(empty)'} for {TYPES[kind]}")
    materials = PLASTIC_MATERIALS if kind in PLASTIC_TYPES else METAL_MATERIALS
    if data["material"] not in materials:
        raise CodingError("material", f"Illegal material code {data['material'] or '(empty)'}")
    if kind in PIN_COUNT_TYPES:
        if data["rows"] not in {"", "1", "2"}:
            raise CodingError("rows", f"Illegal row code {data['rows']}")
        if kind == "S" and data["rows"]:
            raise CodingError("rows", "铁壳 has no row code")
        if not data["pins"]:
            raise CodingError("pins", "Missing pin count")
    elif data["rows"] or data["pins"]:
        raise CodingError("pins", f"{TYPES[kind]} has no pin count")
    if kind in COLOR_TYPES:
        if data["color"] and data["color"] not in COLORS:
            raise CodingError("color", f"Illegal color code {data['color']}")
    elif data["color"]:
        raise CodingError("color", f"{TYPES[kind]} has no color code")
    if kind == "W":
        if data["packaging"] and data["packaging"] not in PACKAGING:
            raise CodingError("packaging", f"Illegal packaging code {data['packaging']}")
        if data["cap"] and data["cap"] not in CAPS:
            raise CodingError("cap", f"Illegal cap code {data['cap']}")
    elif data["packaging"] or data["cap"]:
        raise CodingError("packaging", "Packaging and cap apply to 针座 only")
    if kind in PLATING_TYPES:
        token = f"{data['plating_process']}{data['plating']}"
        if _PLATING.fullmatch(token) is None:
            raise CodingError("plating", f"Illegal plating code {token}")
    elif data["plating_process"] or data["plating"]:
        raise CodingError("plating", f"{TYPES[kind]} has no plating code")
    if kind in SIDE_TYPES:
        if data["side"] and data["side"] not in LOCK_SIDES:
            raise CodingError("side", f"Illegal side code {data['side']}")
    elif data["side"]:
        raise CodingError("side", f"{TYPES[kind]} has no side code")


def _render(data: dict) -> str:
    head = f"{data['pitch']}{data['category']}-{data['serial']}-"
    kind = data["type"]
    core = f"{kind}{data['form']}{data['material']}"
    if kind in PIN_COUNT_TYPES and kind != "S":
        body = head + core + "-" + _pin_token(data)
    elif kind == "S":
        body = head + core + "-" + f"{data['pins']}P"
    elif kind == "C":
        body = head + core
        if data["color"]:
            body += f"-{data['color']}"
    elif kind in PLATING_TYPES:
        body = head + core + "-" + data["plating_process"] + data["plating"]
        if data["side"]:
            body += f"-{data['side']}"
    else:
        body = head + core
    if kind == "W" and (data["packaging"] or data["cap"]):
        body += "-" + data["packaging"] + data["cap"]
    if data["special"]:
        body += "-" + data["special"]
    return body


def _parse(text: str) -> dict:
    pitch_match = re.match(r"^(000|\d+\.\d+)", text)
    if pitch_match is None:
        raise CodingError("pitch", "Pitch must be 000 or a decimal such as 0.5, 1.0, 1.25")
    pitch = pitch_match.group(1)
    rest = text[pitch_match.end() :]
    if not rest:
        raise CodingError("category", "Missing category code")
    category, rest = rest[0], rest[1:]
    if not rest.startswith("-"):
        raise CodingError("serial", "Missing serial")
    serial_match = re.match(r"(\d+|[A-Z]+)(.*)", rest[1:])
    if serial_match is None:
        raise CodingError("serial", "Illegal serial")
    serial, rest = serial_match.group(1), serial_match.group(2)
    if not rest.startswith("-") or len(rest) < 2:
        raise CodingError("type", "Missing type code")
    kind, body = rest[1], rest[2:]
    data = {
        "pitch": pitch,
        "category": category,
        "serial": serial,
        "type": kind,
        "form": "",
        "material": "",
        "rows": "",
        "pins": "",
        "color": "",
        "special": "",
        "packaging": "",
        "cap": "",
        "plating_process": "",
        "plating": "",
        "side": "",
    }
    if kind in PLASTIC_TYPES and kind != "C":
        _parse_counted(data, body, wafer=(kind == "W"))
    elif kind == "C":
        _parse_cover(data, body)
    elif kind == "T":
        _parse_plated(data, body, with_side=False)
    elif kind in SIDE_TYPES:
        _parse_plated(data, body, with_side=True)
    elif kind == "S":
        _parse_shell(data, body)
    elif kind == "K":
        _parse_hook(data, body)
    else:
        raise CodingError("type", f"Illegal type code {kind}")
    return data


def _parse_counted(data: dict, body: str, wafer: bool) -> None:
    form, material, rest = _form_material(body, allow_blank_form=False)
    data["form"] = form
    data["material"] = material
    if rest.startswith("-"):
        rest = rest[1:]
    else:
        raise CodingError("pins", "Missing pin count")
    segments = rest.split("-")
    _read_pins(data, segments[0], allow_color=True)
    extra = segments[1:]
    if wafer and extra and _is_pack_or_cap(extra[0]):
        data["packaging"], data["cap"] = _read_pack_cap(extra[0])
        extra = extra[1:]
    if extra:
        data["special"] = "-".join(extra)
        if data["special"] == "":
            raise CodingError("special", "Empty special code")


def _parse_cover(data: dict, body: str) -> None:
    form, material, rest = _form_material(body, allow_blank_form=False)
    data["form"] = form
    data["material"] = material
    if rest == "":
        return
    if not rest.startswith("-"):
        raise CodingError("color", "Illegal color code")
    segments = rest[1:].split("-")
    head, tail = segments[0], segments[1:]
    if len(head) == 1:
        data["color"] = head
    elif not tail:
        data["special"] = head
    else:
        raise CodingError("color", f"Illegal color code {head}")
    if tail:
        data["special"] = "-".join(tail)
        if data["special"] == "":
            raise CodingError("special", "Empty special code")


def _parse_plated(data: dict, body: str, with_side: bool) -> None:
    form, material, rest = _form_material(body, allow_blank_form=False)
    data["form"] = form
    data["material"] = material
    if not rest.startswith("-") or rest == "-":
        raise CodingError("plating", "Missing plating code")
    segments = rest[1:].split("-")
    process, plating = _read_plating(segments[0])
    data["plating_process"] = process
    data["plating"] = plating
    extra = segments[1:]
    if with_side and extra and extra[0] in {"A", "B"}:
        data["side"] = extra[0]
        extra = extra[1:]
    if extra:
        data["special"] = "-".join(extra)
        if data["special"] == "":
            raise CodingError("special", "Empty special code")


def _parse_shell(data: dict, body: str) -> None:
    form, material, rest = _form_material(body, allow_blank_form=True)
    data["form"] = form
    data["material"] = material
    if not rest.startswith("-"):
        raise CodingError("pins", "Missing pin count")
    segments = rest[1:].split("-")
    _read_pins(data, segments[0], allow_color=False)
    if len(segments) > 1:
        data["special"] = "-".join(segments[1:])
        if data["special"] == "":
            raise CodingError("special", "Empty special code")


def _parse_hook(data: dict, body: str) -> None:
    form, material, rest = _form_material(body, allow_blank_form=True)
    data["form"] = form
    data["material"] = material
    if rest == "":
        return
    if not rest.startswith("-"):
        raise CodingError("material", f"Illegal material code {material}")
    data["special"] = rest[1:]
    if data["special"] == "":
        raise CodingError("special", "Empty special code")


def _form_material(body: str, allow_blank_form: bool) -> tuple[str, str, str]:
    if allow_blank_form and body[:1] in {"A", "B"} and len(body) > 1 and body[1].isdigit():
        return body[0], body[1], body[2:]
    if allow_blank_form and body[:1].isdigit():
        return "", body[0], body[1:]
    if not body:
        raise CodingError("form", "Missing form code")
    if not body[0].isalpha():
        raise CodingError("form", f"Illegal form code {body[0]}")
    if len(body) < 2 or not body[1].isdigit():
        raise CodingError("material", "Illegal material code")
    return body[0], body[1], body[2:]


def _read_pins(data: dict, token: str, allow_color: bool) -> None:
    match = _PINS.fullmatch(token)
    if match is None:
        raise CodingError("pins", f"Illegal pin count {token}")
    rows, pins, color = match.group(1) or "", match.group(2), match.group(3) or ""
    if int(pins) < 1:
        raise CodingError("pins", "Illegal pin count")
    if color and not allow_color:
        raise CodingError("pins", f"Illegal pin count {token}")
    if color and color not in COLORS:
        raise CodingError("color", f"Illegal color code {color}")
    data["rows"] = rows
    data["pins"] = pins
    data["color"] = color


def _read_plating(token: str) -> tuple[str, str]:
    match = _PLATING.fullmatch(token)
    if match is None:
        raise CodingError("plating", f"Illegal plating code {token}")
    return match.group(1), match.group(2)


def _is_pack_or_cap(token: str) -> bool:
    return re.fullmatch(r"[ABC][12]?|[12]", token) is not None


def _read_pack_cap(token: str) -> tuple[str, str]:
    if len(token) == 2:
        return token[0], token[1]
    if token in PACKAGING:
        return token, ""
    return "", token


def _forms(kind: str) -> Mapping:
    if kind in PLASTIC_TYPES:
        return HOUSING_FORMS
    if kind == "T":
        return TERMINAL_FORMS
    if kind in SIDE_TYPES:
        return PIN_FORMS
    if kind == "S":
        return SHELL_FORMS
    if kind == "K":
        return HOOK_FORMS
    return {}


def _pin_token(data: dict) -> str:
    token = f"{data['rows']}x" if data["rows"] else ""
    token += f"{data['pins']}P"
    if data["color"]:
        token += data["color"]
    return token


def _token(value) -> str:
    if value is None:
        return ""
    return str(value).strip().upper()


def _pins(value) -> str:
    if value is None:
        return ""
    text = str(value).strip().upper()
    if text == "":
        return ""
    if text.endswith("P"):
        text = text[:-1]
    if not re.fullmatch(r"\d+", text) or int(text) < 1:
        raise CodingError("pins", f"Illegal pin count {value}")
    return str(int(text))


def _special(value) -> str:
    if value is None:
        return ""
    text = str(value).strip().upper()
    if any(char.isspace() for char in text):
        raise CodingError("special", "Special code cannot contain spaces")
    return text


def _is_row_mark(text: str, index: int) -> bool:
    return (
        index > 0
        and text[index - 1] in "12"
        and index + 1 < len(text)
        and text[index + 1].isdigit()
    )


def _letters(number: int) -> str:
    chars = []
    while number:
        number, remainder = divmod(number - 1, 26)
        chars.append(chr(ord("A") + remainder))
    return "".join(reversed(chars))
