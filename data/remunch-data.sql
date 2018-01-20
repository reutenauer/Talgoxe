CREATE TABLE talgoxe_lemma (id INTEGER PRIMARY KEY AUTO_INCREMENT, lemma VARCHAR(100));
CREATE TABLE talgoxe_type (id INTEGER PRIMARY KEY AUTO_INCREMENT, abbrev VARCHAR(5), name VARCHAR(30));
CREATE TABLE talgoxe_data (id INTEGER PRIMARY KEY AUTO_INCREMENT, d VARCHAR(2000), pos INTEGER, lemma_id INTEGER, type_id INTEGER, CONSTRAINT FOREIGN KEY (lemma_id) REFERENCES talgoxe_lemma (id), CONSTRAINT FOREIGN KEY (type_id) REFERENCES talgoxe_type (id));

INSERT INTO talgoxe_lemma (id, lemma) SELECT l_id, lemma FROM lemma;
INSERT INTO talgoxe_type (id, abbrev, name) SELECT nr, fork, namn FROM typer;
INSERT INTO talgoxe_data (id, d, pos, lemma_id, type_id) SELECT d_id, d, pos, l_id, typ FROM fdata WHERE typ IN (SELECT nr FROM typer) AND l_id IN (SELECT l_id FROM lemma);
