"""python3 -m unittest discover tests (after scripts/build_db.py)"""
import re
import sqlite3
import unittest
from pathlib import Path

DB = Path(__file__).parent.parent / "dist" / "khitan.sqlite"


class Database(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db = sqlite3.connect(DB)

    def one(self, sql, *args):
        return self.db.execute(sql, args).fetchone()[0]

    def test_catalogue_size_matches_otake(self):
        self.assertEqual(self.one("SELECT count(*) FROM grapheme WHERE status='current'"), 368)

    def test_block_size_matches_unicode(self):
        self.assertEqual(self.one("SELECT count(*) FROM character"), 477)

    def test_stated_values_from_the_printed_tables(self):
        for grapheme, value in {"348": "əə", "189": "aa", "339": "ii", "247": "əəd", "139": "naa", "229": "taa",
                                "205": "ənd", "372": "uğʷ", "090": "ʊğʷ", "274": "äğ", "327": "ee"}.items():
            self.assertEqual(self.one("SELECT value FROM primary_reading WHERE grapheme=?", grapheme), value, grapheme)

    def test_unicode_join_samples(self):
        for grapheme, cp in {"001": "18B01", "378": "18B00", "004D": "18B09", "141D": "18CA8"}.items():
            self.assertEqual(self.one("SELECT codepoint FROM grapheme WHERE id=?", grapheme), cp, grapheme)

    def test_codepoints_are_unique_among_graphemes(self):
        self.assertEqual(self.db.execute(
            "SELECT codepoint FROM grapheme WHERE codepoint IS NOT NULL GROUP BY codepoint HAVING count(*)>1").fetchall(), [])

    def test_every_value_names_a_known_source(self):
        known = {r[0] for r in self.db.execute("SELECT id FROM source")}
        for (source,) in self.db.execute("SELECT DISTINCT source FROM reading"):
            self.assertIn(source.split(":")[0], known)

    def test_mnemonic_readings_are_not_marked_phonetic(self):
        self.assertEqual(self.one("SELECT count(*) FROM reading WHERE source='kane2009' AND kind='phonetic' AND value GLOB '*[ảẻỉỏủ]*'"), 0)

    def test_rhyme_scans_stay_in_their_document(self):
        self.assertEqual(self.one("SELECT reading FROM rhyme WHERE document='B.CAL' AND verse='2'"), "tuu")

    def test_loan_spelling_keeps_its_hanzi(self):
        self.assertEqual(self.one("SELECT transliteration FROM loan_spelling WHERE hanzi='檀'"), "taan")

    def test_paper_tables_keep_their_notation(self):
        for source, grapheme, value in (("otake2018", "122", "ay"), ("otake2018", "254", "ed"), ("otake2015", "229", "tā"), ("otake2025", "226", "ɵ̈ɵ̈")):
            self.assertEqual(self.one("SELECT count(*) FROM reading WHERE source=? AND grapheme=? AND value=?", source, grapheme, value), 1, grapheme)

    def test_later_published_table_leads_the_primary_reading(self):
        self.assertEqual(self.one("SELECT value FROM primary_reading WHERE grapheme='226'"), "ɵ̈ɵ̈")

    def test_dissertation_record_states_its_availability(self):
        self.assertIn('abstracts only', self.one("SELECT terms FROM source WHERE id='otake2020'"))

    def test_classics_paper_is_cited_by_the_cognates(self):
        self.assertIn('KOTONOHA', self.one("SELECT citation FROM source WHERE id='otake2015c'"))
        for form in ('mɵɵr', 'yaw-'):
            self.assertIn('2015c', self.one("SELECT cf FROM cognate WHERE form=?", form))

    def test_example_sentence_keeps_transcription_and_citation(self):
        self.assertEqual(self.one("SELECT citation FROM example WHERE n=2"), "B.CAL 10‒11")
        self.assertEqual(self.one("SELECT transcription FROM example_word WHERE n=2 AND line=1 AND position=1"), "miin")

    def test_spelling_ids_exist(self):
        known = {r[0] for r in self.db.execute("SELECT id FROM grapheme")}
        for table in ("rhyme", "loan_spelling", "form", "cognate"):
            for (spelling,) in self.db.execute(f"SELECT spelling FROM {table} WHERE spelling<>''"):
                for gid in re.findall(r"\S+", spelling.replace("~", " ")):
                    self.assertIn(gid, known, f"{table}: {spelling}")


if __name__ == "__main__":
    unittest.main()
