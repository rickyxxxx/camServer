import pyodbc


class Database:

    def __init__(self) -> None:
        self.conn = pyodbc.connect(
            "DRIVER={ODBC Driver 18 for SQL Server};"
            "SERVER=localhost,1433;"
            "DATABASE=CamServer;"
            "UID=sa;"
            "PWD=Server@2025;"
            "Encrypt=yes;"
            "TrustServerCertificate=yes;"
        )
        self.cursor = self.conn.cursor()

    def fetch(self, cmd: str) -> any:
        rows = self.cursor.fetchall()
        for row in rows:
            print(row)

    def execute(self, cmd: str, values: tuple) -> None:
        self.cursor.execute(cmd, values)
        self.conn.commit()

    def insert_image(self, image_path: str, spec: dict) -> None:
        cmd = ("INSERT INTO Images (CamID, [Datetime], BitDepth, Gain, ExpTime, GeoLoc, ImgPath) "
               "VALUES (?, ?, ?, ?, ?, geography::STGeomFromText(?, 4326), ?)")
        geo = f"POINT({spec["lng"]} {spec["lat"]})"
        values = spec["id"], spec["date"], spec['bit'], spec["gain"], spec['exp'], geo, image_path
        self.execute(cmd, values)

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    path = "/mnt/CamData/images/"
    spec = {"id": "123456", "date": "2025-01-01T01:01:01.213", "bit": 16, "gain": 1, "exp": 250_000, "lat": 34.42083, "lng": -119.69819}
    db = Database()
    db.insert_image(path, spec)
    db.close()

""" 
DECLARE @currentLocation GEOGRAPHY = geography::STPointFromText('POINT(-73.985428 40.748817)', 4326); -- Example: Times Square, NY
DECLARE @radius FLOAT = 1000; -- Distance in meters

SELECT Name, Coordinates.ToString() AS Coordinates
FROM Locations
WHERE Coordinates.STDistance(@currentLocation) <= @radius;
"""