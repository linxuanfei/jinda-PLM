"""B05 examples, illegal codes, and global part-number dedupe."""

import unittest

from plugins.jinda_connector_coding.coding import (
    HOOK_FORMS,
    CodingError,
    DuplicatePartNumber,
    create_part_number,
    generate,
    import_part_number,
    next_serial,
    screen_ipn,
    validate,
)

EXAMPLES = [
    (
        "胶壳",
        {
            "pitch": "1.0",
            "category": "T",
            "serial": "1",
            "type": "Y",
            "form": "O",
            "material": "1",
            "rows": "2",
            "pins": "5",
            "color": "A",
        },
        "1.0T-1-YO1-2x5PA",
    ),
    (
        "针座",
        {
            "pitch": "1.0",
            "category": "T",
            "serial": "1",
            "type": "W",
            "form": "L",
            "material": "4",
            "rows": "2",
            "pins": "5",
            "color": "B",
            "packaging": "A",
            "cap": "1",
            "special": "S",
        },
        "1.0T-1-WL4-2x5PB-A1-S",
    ),
    (
        "胶芯",
        {
            "pitch": "1.0",
            "category": "T",
            "serial": "1",
            "type": "B",
            "form": "L",
            "material": "4",
            "rows": "2",
            "pins": "5",
            "color": "B",
            "special": "S",
        },
        "1.0T-1-BL4-2x5PB-S",
    ),
    (
        "盖子",
        {
            "pitch": "1.0",
            "category": "T",
            "serial": "1",
            "type": "C",
            "form": "O",
            "material": "3",
            "color": "B",
        },
        "1.0T-1-CO3-B",
    ),
    (
        "端子",
        {
            "pitch": "1.0",
            "category": "T",
            "serial": "1",
            "type": "T",
            "form": "L",
            "material": "2",
            "plating_process": "A",
            "plating": "1",
        },
        "1.0T-1-TL2-A1",
    ),
    (
        "铁壳",
        {
            "pitch": "1.0",
            "category": "T",
            "serial": "4",
            "type": "S",
            "form": "A",
            "material": "3",
            "pins": "30",
        },
        "1.0T-4-SA3-30P",
    ),
    (
        "卡钩",
        {
            "pitch": "1.0",
            "category": "T",
            "serial": "4",
            "type": "K",
            "form": "A",
            "material": "3",
        },
        "1.0T-4-KA3",
    ),
    (
        "端子PIN",
        {
            "pitch": "1.0",
            "category": "T",
            "serial": "1",
            "type": "P",
            "form": "L",
            "material": "2",
            "plating_process": "A",
            "plating": "1",
            "side": "A",
        },
        "1.0T-1-PL2-A1-A",
    ),
    (
        "锁扣",
        {
            "pitch": "1.0",
            "category": "T",
            "serial": "1",
            "type": "M",
            "form": "L",
            "material": "1",
            "plating_process": "A",
            "plating": "1",
            "side": "A",
        },
        "1.0T-1-ML1-A1-A",
    ),
    (
        "拉扣",
        {
            "pitch": "1.0",
            "category": "F",
            "serial": "1",
            "type": "D",
            "form": "L",
            "material": "4",
            "rows": "2",
            "pins": "5",
            "color": "B",
        },
        "1.0F-1-DL4-2x5PB",
    ),
    (
        "套子",
        {
            "pitch": "2.0",
            "category": "T",
            "serial": "15",
            "type": "U",
            "form": "H",
            "material": "6",
            "rows": "2",
            "pins": "3",
            "color": "D",
        },
        "2.0T-15-UH6-2x3PD",
    ),
    (
        "Insert",
        {
            "pitch": "0.5",
            "category": "Y",
            "serial": "01",
            "type": "N",
            "form": "C",
            "material": "8",
            "rows": "2",
            "pins": "12",
            "color": "B",
        },
        "0.5Y-01-NC8-2x12PB",
    ),
]


class B05Examples(unittest.TestCase):
    def test_examples_generate_and_validate(self):
        for name, fields, expected in EXAMPLES:
            with self.subTest(name=name):
                self.assertEqual(generate(fields), expected)
                parsed = validate(expected)
                self.assertEqual(generate(parsed), expected)
                self.assertNotIn("Y01", expected)
                self.assertNotIn("C03", expected)

    def test_letter_o_and_hook_sides(self):
        self.assertIn("YO1", generate(EXAMPLES[0][1]))
        self.assertIn("CO3", generate(EXAMPLES[3][1]))
        with self.assertRaises(CodingError) as raised:
            generate({**EXAMPLES[0][1], "form": "0"})
        self.assertEqual(raised.exception.field, "form")
        self.assertEqual(HOOK_FORMS["A"], "左卡钩")
        self.assertEqual(HOOK_FORMS["B"], "右卡钩")
        right = generate({**EXAMPLES[6][1], "form": "B"})
        self.assertEqual(right, "1.0T-4-KB3")
        self.assertEqual(validate(right)["form"], "B")

    def test_serial_is_not_padded(self):
        self.assertEqual(next_serial("T", []), "1")
        self.assertEqual(next_serial("T", ["1", "2"]), "3")
        self.assertEqual(next_serial("F", []), "A")
        self.assertEqual(next_serial("F", ["A"]), "B")
        self.assertEqual(next_serial("Y", ["1"]), "2")
        self.assertEqual(generate(EXAMPLES[10][1]), "2.0T-15-UH6-2x3PD")
        self.assertEqual(generate(EXAMPLES[11][1]), "0.5Y-01-NC8-2x12PB")

    def test_special_text_is_kept(self):
        fields = {**EXAMPLES[0][1], "special": "X1"}
        code = generate(fields)
        self.assertEqual(code, "1.0T-1-YO1-2x5PA-X1")
        self.assertEqual(validate(code)["special"], "X1")


class B05Rejections(unittest.TestCase):
    def test_illegal_category(self):
        with self.assertRaises(CodingError) as raised:
            validate("1.0Z-1-YO1-2x5PA")
        self.assertEqual(raised.exception.field, "category")

    def test_illegal_type(self):
        with self.assertRaises(CodingError) as raised:
            validate("1.0T-1-QO1-2x5PA")
        self.assertEqual(raised.exception.field, "type")

    def test_illegal_material(self):
        with self.assertRaises(CodingError) as raised:
            validate("1.0T-1-TL9-A1")
        self.assertEqual(raised.exception.field, "material")

    def test_illegal_color(self):
        with self.assertRaises(CodingError) as raised:
            validate("1.0T-1-YO1-2x5PK")
        self.assertEqual(raised.exception.field, "color")

    def test_illegal_plating_process(self):
        with self.assertRaises(CodingError) as raised:
            validate("1.0T-1-TL2-C1")
        self.assertEqual(raised.exception.field, "plating")

    def test_illegal_plating_material(self):
        with self.assertRaises(CodingError) as raised:
            validate("1.0T-1-TL2-A9")
        self.assertEqual(raised.exception.field, "plating")


class PartNumberPool(unittest.TestCase):
    def test_create_refuses_an_existing_b05_number(self):
        code = "1.0T-1-YO1-2x5PA"
        with self.assertRaises(DuplicatePartNumber):
            create_part_number(EXAMPLES[0][1], [code])

    def test_import_refuses_an_existing_legacy_number(self):
        with self.assertRaises(DuplicatePartNumber):
            import_part_number("OLD-FACTORY-9", ["old-factory-9"])
        with self.assertRaises(DuplicatePartNumber):
            screen_ipn("OLD-FACTORY-9", ["old-factory-9"])

    def test_new_numbers_still_see_the_legacy_pool(self):
        pool = ["OLD-FACTORY-9"]
        created = create_part_number(EXAMPLES[0][1], pool)
        self.assertEqual(created, "1.0T-1-YO1-2x5PA")
        self.assertEqual(import_part_number("OLD-FACTORY-8", pool), "OLD-FACTORY-8")
        with self.assertRaises(DuplicatePartNumber):
            create_part_number(EXAMPLES[0][1], pool + [created])
        with self.assertRaises(DuplicatePartNumber):
            screen_ipn(created, [created])
        with self.assertRaises(CodingError):
            screen_ipn("1.0T-1-YO1-2x5PK", [])

    def test_blank_ipn_is_not_a_number(self):
        self.assertIsNone(screen_ipn("", []))
        self.assertIsNone(screen_ipn(None, ["1.0T-1-YO1-2x5PA"]))


if __name__ == "__main__":
    unittest.main()
