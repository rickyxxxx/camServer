from typing import List, Dict, Any

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

    def query(self, query: str) -> list:
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def execute(self, cmd: str, *values: tuple) -> None:
        # self.cursor.execute(cmd, values)
        self.cursor.execute(cmd)
        self.conn.commit()

    def insert_image(self, image_path: str, spec: dict) -> None:
        cmd = ("INSERT INTO Images (CamID, CamName, [Datetime], BitDepth, Gain, ExpTime, GeoLoc, ImgPath) "
               "VALUES (?, ?, ?, ?, ?, ?, geography::STGeomFromText(?, 4326), ?)")
        geo = f"POINT({spec["lng"]} {spec["lat"]})"
        values = spec["id"], spec["name"], spec["date"], spec['bit'], spec["gain"], spec['exp'], geo, image_path
        self.execute(cmd, values)

    def insert_temp_humidity(self, spec: dict) -> None:
        cmd = "INSERT INTO TempHumidity VALUES (?, ?, ?, ?)"
        values = spec['id'], spec['date'], spec['temp'], spec['humidity']
        self.execute(cmd, values)

    def search_images_by_date(self, datetime_periods: list[tuple[str, str]] = None) -> list[dict[str, str]]:
        # generate the sql search command
        columns = ['ImgPath', "CamName", "Datetime", "ExpTime", "Gain", "BitDepth"]
        sql = f"SELECT {",".join(columns)} FROM Images "

        if datetime_periods:
            period_conditions = " OR ".join([
                f"[Datetime] BETWEEN '{start}' AND '{end}'"
                for start, end in datetime_periods
            ])
            sql += f"WHERE ({period_conditions})"

        sql += "ORDER BY [Datetime] DESC"

        # columns = ['ImgPath', "CamName", "Datetime", "ExpTime", "Gain", ]

        res = self.query(sql)
        return [dict(zip(columns, row)) for row in res]

    def close(self):
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    import numpy as np
    db = Database()
    data = db.query('SELECT [Datetime], Humidity, Temperature FROM TempHumidity ORDER BY [Datetime] DESC;')
    data = np.array(data)
    dates = data[:, 0]
    temp = data[:, 1].astype(np.float32)
    humidity = data[:, 2].astype(np.float32)
    plt.plot(dates, humidity)
    plt.title("humidity vs. time")
    plt.ylabel("percentage (%)")
    plt.xticks(rotation=30)  # Rotate x-axis labels
    plt.subplots_adjust()

    plt.savefig('humidity.png')
    plt.clf()
    plt.plot(dates, temp)
    plt.title("temperature vs. time")
    plt.ylabel("C")
    plt.xticks(rotation=30)  # Rotate x-axis labels
    plt.subplots_adjust()
    plt.savefig('temp.png')
    db.close()

""" 
DECLARE @currentLocation GEOGRAPHY = geography::STPointFromText('POINT(-73.985428 40.748817)', 4326); -- Example: Times Square, NY
DECLARE @radius FLOAT = 1000; -- Distance in meters

SELECT Name, Coordinates.ToString() AS Coordinates
FROM Locations
WHERE Coordinates.STDistance(@currentLocation) <= @radius;
"""