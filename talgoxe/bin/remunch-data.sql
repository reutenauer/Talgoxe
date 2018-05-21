/*
  Not using migration; instead dump the SQL, remove the AUTO_INCREMENT FROM primary keys,
  and copy the existing table into them.  For Data (table fdata), this is needed:
  INSERT INTO talgoxe_data (id, d, pos, lemma_id, type_id) SELECT d_id, d, pos, l_id, typ FROM fdata WHERE typ IN (SELECT nr FROM typer) AND l_id IN (SELECT l_id FROM lemma);
  Foreign keys fails otherwise!
*/
CREATE TABLE talgoxe_artikel (id INTEGER PRIMARY KEY AUTO_INCREMENT, lemma VARCHAR(100), rang INTEGER, skapat DATETIME, uppdaterat DATETIME);
CREATE TABLE talgoxe_typ (id INTEGER PRIMARY KEY AUTO_INCREMENT, kod VARCHAR(5), namn VARCHAR(30), skapat DATETIME, uppdaterat DATETIME);
CREATE TABLE talgoxe_spole (id INTEGER PRIMARY KEY AUTO_INCREMENT, text VARCHAR(2000), pos INTEGER, artikel_id INTEGER, typ_id INTEGER, skapat DATETIME, uppdaterat DATETIME, CONSTRAINT FOREIGN KEY (artikel_id) REFERENCES talgoxe_artikel (id), CONSTRAINT FOREIGN KEY (typ_id) REFERENCES talgoxe_typ (id));

INSERT INTO talgoxe_artikel (id, lemma, rang) SELECT l_id, lemma, hom FROM lemma WHERE l_id > 0;
INSERT INTO talgoxe_typ (id, kod, namn) SELECT nr, fork, namn FROM typer WHERE nr > 0; /* id = 0 är besvärligt! (SO) */
INSERT INTO talgoxe_spole (id, text, pos, artikel_id, typ_id) SELECT d_id, d, pos, l_id, typ FROM fdata WHERE typ IN (SELECT nr FROM typer) AND d_id > 0 AND l_id IN (SELECT l_id FROM lemma);

INSERT INTO talgoxe_typ (kod, namn) VALUES ('og', 'Ogiltig');
