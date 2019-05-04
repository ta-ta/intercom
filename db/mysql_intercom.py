# coding: UTF-8

from database import Database

class Database_intercom(Database):
    def __init__(self, dbconfig, unlabeled=False):
        super(Database_intercom, self).__init__(dbconfig)

    # テーブル作成
    def create_masters_table(self):
        """ masters テーブルを作成 """
        try:
            query = """
                CREATE TABLE IF NOT EXISTS masters (
                    master_id mediumint unsigned not null auto_increment,
                    filename text not null,
                    PRIMARY KEY (master_id)
                ) ENGINE=INNODB
                """
            self.cursor.execute(query)
            self.connect.commit()
        except:
            self.connect.rollback()
            raise

    def create_fingerprints_table(self):
        """ fingerprints テーブルを作成 """
        try:
            query = """
                CREATE TABLE IF NOT EXISTS fingerprints (
                    hash binary(4) not null,
                    master_id mediumint unsigned not null,
                    offset int unsigned not null,
                    INDEX (hash),
                    UNIQUE (master_id, offset, hash),
                    FOREIGN KEY (master_id) REFERENCES masters (master_id) ON DELETE CASCADE
                ) ENGINE=INNODB
            """
            self.cursor.execute(query)
            self.connect.commit()
        except:
            self.connect.rollback()
            raise

    # masters
    def insert_master(self, filename):
        """ masterに追加 """
        try:
            query = """
                INSERT IGNORE INTO masters (filename)
                VALUES (?)
            """
            self.cursor.execute(query, [filename])
            self.connect.commit()
        except:
            self.connect.rollback()
            raise
        master_id = self.cursor.lastrowid
        return master_id


    # fingerprints
    def insert_fingerprints(self, master_id, hash_offset):
        """ fingerprintsに追加 """
        insert_values = []
        for hash, offset in hash_offset:
            insert_values.extend([hash, master_id, int(offset)])
        try:
            query = """
                INSERT IGNORE INTO fingerprints (hash, master_id, offset)
                VALUES {values}
            """.format(values=','.join(["(UNHEX(?), ?, ?)"] * len(hash_offset)))
            self.cursor.execute(query, insert_values)
            self.connect.commit()
        except:
            self.connect.rollback()
            raise

    def fetch_master_id_by_hashes(self, hashes):
        """ hashに紐づくfingerprint情報を取得 """
        query = """
            SELECT HEX(hash) as hash, master_id, offset
            FROM fingerprints
            WHERE hash IN ({hashes})
        """.format(hashes=','.join(['UNHEX(?)'] * len(hashes)))
        self.cursor.execute(query, hashes)
        fetch_data = self.cursor.fetchall()
        return fetch_data
