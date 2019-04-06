import sqlite3

karmadatabase = sqlite3.connect('karma.db')
kcursor = karmadatabase.cursor()
kcursor.executescript("""
	CREATE TABLE if not exists karma(
		id unsigned big int PRIMARY KEY,
		name text NOT NULL,
		karma int DEFAULT 0,
		karma_given int DEFAULT 0,
		last_given date
	);

	CREATE INDEX if not exists kscore
	ON karma (karma, karma_given);
""")

karmadatabase.commit()

ranks_dirty = True

def rebuild_ranks():
	global ranks_dirty
	if not ranks_dirty:
		return
	
	# UPDATE karma set karma = -9001
	# where id = 189938411350523904 and karma > 9000;
	kcursor.executescript("""
		DROP TABLE if exists tempranks;

		CREATE TEMP TABLE tempranks AS
		SELECT id, name, karma, karma_given
		FROM karma
		ORDER BY karma DESC, karma_given DESC;

		DROP TABLE if exists ranks;

		CREATE TABLE ranks AS
		SELECT _ROWID_ as row, id, name, karma, karma_given
		from tempranks;

		DROP TABLE tempranks;
	""")
	ranks_dirty = False

def get_data(userid):
	kcursor.execute('SELECT * FROM karma where id=?;',(userid,))
	return kcursor.fetchone()

def set_karma(user, karma):
	global ranks_dirty
	ranks_dirty = True
	kcursor.execute(
		'INSERT or IGNORE INTO karma (id, name, karma) VALUES (?, ?, ?);',
		(user.id, user.name, karma)
	)
	kcursor.execute(
		'UPDATE karma SET name=?, karma=? where ID=?;',
		(user.name, karma, user.id)
	)

def set_karma_given(user, karma_given, last_given):
	global ranks_dirty
	ranks_dirty = True
	kcursor.execute(
	"""
		INSERT or IGNORE INTO karma (id, name, karma_given, last_given)
		VALUES (?, ?, ?, ?);
	""",
		(user.id, user.name, karma_given, last_given)
	)
	kcursor.execute(
	"""
		UPDATE karma SET name=?, karma_given=?, last_given=?
		WHERE ID=?;
	""",
		(user.name, karma_given, last_given, user.id)
	)

def get_rank(userid):
	rebuild_ranks()
	kcursor.execute('SELECT row from ranks where id=?;',(userid,))
	return kcursor.fetchone()

def get_ranks(users):
	rebuild_ranks()
	if len(users)==0:
		return []
	que = ",".join("?" for _ in users)
	ids = tuple([user.id for user in users])
	kcursor.execute(f"""
		SELECT  _ROWID_ as row, name, karma, karma_given
		FROM ranks
		where id in ({que});
	""", ids)
	return kcursor.fetchall()

def get_top(best_rank, count):
	rebuild_ranks()
	kcursor.execute("""
		SELECT row, name, karma, karma_given
		FROM ranks
		WHERE row >= ?
		LIMIT ?;
	""", (best_rank, count))
	return kcursor.fetchall()

def reset_karma():
	kcursor.executescript("""
		DROP INDEX if exists kscore;
		DROP TABLE if exists karma;

		CREATE TABLE if not exists karma(
			id unsigned big int PRIMARY KEY,
			name text NOT NULL,
			karma int DEFAULT 0,
			karma_given int DEFAULT 0,
			last_given date
		);

		CREATE INDEX if not exists kscore
		ON karma (karma, karma_given);
	""")

def commit():
	karmadatabase.commit()
