import mysql.connector


class DB:

    def __init__(self):
        self.config = {
            'user': 'root',
            'password': 'kica',
            'host': '127.0.0.1',
            'database': 'san_diego'
        }
        self.cnx = mysql.connector.connect(**self.config)

    def insertData(self, obj):
        cursor = self.cnx.cursor()
        q = ("INSERT INTO records VALUES(null, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
        data = (obj['record_date'].date(), obj['doc_number'], obj['doc_type'], obj['role'], obj['grantor'], obj['grantee'], obj['apn'], obj['county'], obj['state'])
        cursor.execute(q, data)
        self.cnx.commit()
        cursor.close()
