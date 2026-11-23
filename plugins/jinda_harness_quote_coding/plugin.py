"""Empty extension point for wire-harness sample-quote numbering (线束打样报价编码).

No numbering rules are defined. This module does not generate, parse, or
validate a code.
"""

from plugin import InvenTreePlugin


class JindaHarnessQuoteCodingPlugin(InvenTreePlugin):
    """Reserved plugin. No mixins and no numbering behavior."""

    NAME = "JindaHarnessQuoteCoding"
    SLUG = "jinda-harness-quote-coding"
    TITLE = "津达立线束打样报价编码"
    AUTHOR = "津达立电子"
    DESCRIPTION = (
        "Empty extension point for wire-harness sample-quote numbering. "
        "No coding rules are implemented."
    )
    VERSION = "0.0.0"
    WEBSITE = "https://github.com/linxuanfei/jinda-PLM"
    LICENSE = "MIT"
