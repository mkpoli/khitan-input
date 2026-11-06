-- A grapheme is Otake's catalogue number. A character is a Unicode code point.
-- Every value keeps its source; nothing here merges scholars into one reading.

CREATE TABLE source (id TEXT PRIMARY KEY, citation TEXT NOT NULL, url TEXT, retrieved TEXT, terms TEXT, note TEXT);

CREATE TABLE character (
  codepoint TEXT PRIMARY KEY, text TEXT NOT NULL, name TEXT NOT NULL, radical_group TEXT,
  jurchen_tentative INTEGER NOT NULL  -- NamesList: tentatively Jurchen Small Script
);
CREATE TABLE catalogue_number (codepoint TEXT NOT NULL REFERENCES character, scheme TEXT NOT NULL, value TEXT NOT NULL);

CREATE TABLE grapheme (
  id TEXT PRIMARY KEY,
  status TEXT NOT NULL,      -- current | variant | renumbered | sequence | void | uncatalogued
  target TEXT,               -- variant: the grapheme it varies; renumbered: new number; sequence: its parts
  number_origin TEXT,        -- 1985 | derived (D) | otake (C)
  codepoint TEXT REFERENCES character,
  unicode_method TEXT,       -- west_1985_number | west_1985_renumbered | visual
  unicode_confidence TEXT,
  unicode_candidate TEXT     -- weak match only, not used for text
);

CREATE TABLE reading (
  grapheme TEXT, codepoint TEXT, source TEXT NOT NULL, value TEXT NOT NULL,
  kind TEXT NOT NULL,        -- phonetic | semantic | mnemonic
  value_type TEXT,           -- V | VC | VCC | CV | CVC
  tier TEXT NOT NULL,        -- stated | stated_tentative | stated_unattested | aligned_spelling | single_grapheme_word | scholar | scholar_via_n4725r
  location TEXT, page INTEGER
);
CREATE INDEX reading_grapheme ON reading(grapheme);
CREATE INDEX reading_codepoint ON reading(codepoint);
CREATE TABLE primary_reading (grapheme TEXT PRIMARY KEY, value TEXT NOT NULL, tier TEXT NOT NULL, source TEXT NOT NULL, page INTEGER);
CREATE TABLE relation (codepoint TEXT NOT NULL, type TEXT NOT NULL, other TEXT NOT NULL, source TEXT NOT NULL);

CREATE TABLE document (id TEXT PRIMARY KEY, script TEXT NOT NULL, abbreviation TEXT, title TEXT, date_text TEXT, year INTEGER, khitan_lines INTEGER, cf TEXT, page INTEGER);
CREATE TABLE attestation (kind TEXT NOT NULL, ref INTEGER NOT NULL, document TEXT NOT NULL, line TEXT NOT NULL);
CREATE INDEX attestation_ref ON attestation(kind, ref);

CREATE TABLE form (id INTEGER PRIMARY KEY, source TEXT NOT NULL, spelling TEXT NOT NULL, text TEXT, segmentation TEXT, transcription TEXT, gloss TEXT, note TEXT, page INTEGER);
CREATE TABLE rhyme (id INTEGER PRIMARY KEY, document TEXT, lines TEXT, stanza TEXT, verse TEXT, spelling TEXT, text TEXT, reading TEXT, note TEXT, page INTEGER);
CREATE TABLE cognate (n INTEGER PRIMARY KEY, form TEXT, spelling TEXT, text TEXT, pos TEXT, gloss TEXT, cf TEXT, page INTEGER);
CREATE TABLE cognate_reflex (n INTEGER NOT NULL REFERENCES cognate, language TEXT NOT NULL, text TEXT NOT NULL);
CREATE TABLE loan_spelling (id INTEGER PRIMARY KEY, section TEXT, hanzi TEXT, spelling TEXT, text TEXT, transliteration TEXT, page INTEGER);
CREATE TABLE loan_use (spelling_id INTEGER NOT NULL REFERENCES loan_spelling, use TEXT NOT NULL);
CREATE TABLE bibliography (section TEXT, entry TEXT NOT NULL, page INTEGER);
CREATE TABLE erratum (glyph TEXT NOT NULL, printed_label TEXT NOT NULL, page INTEGER);  -- glyph and printed number disagree in the source

CREATE TABLE large_reading (number INTEGER PRIMARY KEY, babelstone_pua TEXT, reconstruction TEXT, chinese_transcription TEXT, meaning TEXT, source TEXT NOT NULL);

CREATE TABLE example (n INTEGER PRIMARY KEY, source TEXT NOT NULL, citation TEXT, translation TEXT, note TEXT, page INTEGER);
CREATE TABLE example_line (n INTEGER NOT NULL REFERENCES example, line INTEGER NOT NULL, transcription TEXT, gloss TEXT);
CREATE TABLE example_word (n INTEGER NOT NULL REFERENCES example, line INTEGER NOT NULL, position INTEGER NOT NULL, spelling TEXT, text TEXT, transcription TEXT);
