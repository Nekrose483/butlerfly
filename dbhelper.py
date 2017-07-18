import sqlite3


class DBHelper:
    def __init__(self, dbname="DroneDatabase.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname)

    def setup(self):
        tblstmt = "CREATE TABLE IF NOT EXISTS drones (id text, drone text)"
        droneididx = "CREATE INDEX IF NOT EXISTS droneidIndex ON drones (id ASC)"
        droneidx = "CREATE INDEX IF NOT EXISTS droneIndex ON drones (drone ASC)"
        self.conn.execute(tblstmt)
        self.conn.execute(droneididx)
        self.conn.execute(droneidx)
        self.conn.commit()

    def add_item(self, droneID, drone):
        stmt = "INSERT INTO drones (droneID, drone) VALUES (?, ?)"
        args = (droneID, drone)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_item(self, drone):
        stmt = "DELETE FROM drones WHERE drone = (?)"
        args = (drone)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_id(self, drone):
        stmt = "SELECT id text FROM drones WHERE drone = (?)"
        args = (drone)
        return [x[0] for x in self.conn.execute(stmt, args)]