"""B05 connector part numbers (津达电子连接器产品料号编码原则, 2026-08-03).

Generate and validate live in ``coding.py``. When this plugin is enabled,
saving a Part IPN rejects an illegal B05 number and rejects any number that
already exists on another part, including a legacy number that is not B05.
"""

from plugin import InvenTreePlugin
from plugin.mixins import ValidationMixin

from .coding import CodingError, DuplicatePartNumber, generate, screen_ipn, validate


class JindaConnectorCodingPlugin(ValidationMixin, InvenTreePlugin):
    """B05 connector coding. Disabled until a staff user enables it."""

    NAME = "JindaConnectorCoding"
    SLUG = "jinda-connector-coding"
    TITLE = "津达立连接器编码"
    AUTHOR = "津达立电子"
    DESCRIPTION = (
        "B05 connector part numbers: generate, validate, and refuse a number "
        "that already exists."
    )
    VERSION = "0.1.0"
    WEBSITE = "https://github.com/linxuanfei/jinda-PLM"
    LICENSE = "MIT"

    def generate_part_number(self, **fields) -> str:
        return generate(fields)

    def validate_part_number(self, code: str) -> dict:
        return validate(code)

    def validate_part_ipn(self, ipn: str, part):
        matches = _other_ipns(ipn, part)
        try:
            screen_ipn(ipn, matches)
        except (CodingError, DuplicatePartNumber) as exc:
            self.raise_error(str(exc))
        return None


def _other_ipns(ipn, part) -> list[str]:
    if ipn is None or str(ipn).strip() == "":
        return []
    from part.models import Part

    rows = Part.objects.filter(IPN__iexact=str(ipn).strip())
    if getattr(part, "pk", None):
        rows = rows.exclude(pk=part.pk)
    return list(rows.values_list("IPN", flat=True))
