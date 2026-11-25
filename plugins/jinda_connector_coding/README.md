# 津达立连接器编码 / Jinda connector part numbering

B05（2026-08-03）《津达电子连接器产品料号编码原则》.

`coding.py` generates a part number from fields, validates a candidate, and refuses a number that is already in the pool passed to it. The pool must include legacy numbers that are not B05. `JindaConnectorCodingPlugin` applies that check to the Part IPN when the plugin is enabled.

Discovered plugins stay off until a staff user enables **津达立连接器编码** in the InvenTree Admin Center. Do not load the InvenTree demo data set.

卡钩 position ⑤ is A = 左卡钩, B = 右卡钩. 通用型 is the letter O. 特殊代码 is free text. 流水 is not zero-padded.
