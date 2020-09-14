DROP TABLE IF EXISTS channel;
DROP TABLE IF EXISTS programme;

CREATE TABLE channel (
  ch_id TEXT UNIQUE NOT NULL,
  disp_name TEXT UNIQUE NOT NULL,
  disp_name_l TEXT UNIQUE NOT NULL,
  icon TEXT
);

CREATE TABLE programme (
  channel TEXT NOT NULL,
  pstart TIMESTAMP NOT NULL,
  pstop TIMESTAMP NOT NULL,
  title TEXT,
  pdesc TEXT,
  cat TEXT,
  FOREIGN KEY (channel) REFERENCES channel (ch_id)
);
