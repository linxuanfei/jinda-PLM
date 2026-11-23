"""Empty extension point for connector part numbering (连接器编码).

No numbering rules are defined. This module does not generate, parse, or
validate a code.
"""

from plugin import InvenTreePlugin


class JindaConnectorCodingPlugin(InvenTreePlugin):
    """Reserved plugin. No mixins and no numbering behavior."""

    NAME = "JindaConnectorCoding"
    SLUG = "jinda-connector-coding"
    TITLE = "津达立连接器编码"
    AUTHOR = "津达立电子"
    DESCRIPTION = (
        "Empty extension point for connector part numbering. "
        "No coding rules are implemented."
    )
    VERSION = "0.0.0"
    WEBSITE = "https://github.com/linxuanfei/jinda-PLM"
    LICENSE = "MIT"
