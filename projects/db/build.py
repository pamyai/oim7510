#try1

database = mo.notebook_dir() / "database.duckdb"

def ask(sql):
    with duckdb.connect(database, read_only=True) as _con:
        return _con.sql(sql).pl()
        