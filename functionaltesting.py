import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine



def connectToDatabase(query):
    engine = create_engine("mysql://root:Aaron101702@localhost/mco1datawarehouse")
    with engine.connect() as conn, conn.begin():
        return pd.read_sql(query, conn)



query1 = "SELECT c.region_name, c.province, c.city, YEAR(a.queuedate) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus = \"COMPLETE\" AND NOT YEAR(a.queuedate)=1970 GROUP BY c.region_name, c.province, c.city, YEAR(a.queuedate) WITH ROLLUP ORDER BY c.region_name, c.province, c.city, appointment_year;"
query3 = "SELECT DAYOFWEEK(apptdate) AS \"day_of_appointment\", D.city, D.province, D.region_name, AVG(D.appts) FROM (SELECT c.city, c.province, c.region_name, DATE(a.queuedate) as apptdate, COUNT(a.apptid) AS appts FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE YEAR(a.queuedate) <> 1970 GROUP BY DATE(a.queuedate), c.city, c.province, c.region_name) D GROUP BY DAYOFWEEK(apptdate), D.city, D.province, D.region_name WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.city, D.province, D.region_name;"
query4 = "SELECT d.mainspecialty, p.agerange, p.age, a.isvirtual, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(MINUTE, a.starttime, a.endtime)) AS average_appointment_duration_minutes FROM appointments a JOIN patients p ON a.pxid = p.pxid JOIN doctors d ON a.doctorid = d.doctorid WHERE YEAR(a.starttime) <> 1970 AND YEAR(a.endtime) <> 1970 AND a.apptstatus = \"COMPLETE\" AND p.agerange <> \"INVALID\" GROUP BY d.mainspecialty, p.agerange, p.age, a.isvirtual WITH ROLLUP ORDER BY d.mainspecialty, p.agerange, p.age, a.isvirtual;"
query1_df = connectToDatabase(query1)
query3_df = connectToDatabase(query3)
query4_df = connectToDatabase(query4)


print(query1_df)
print(query3_df)
print(query4_df)

#WHERE A.appointment_year = 2020 AND A.region_name IS NOT NULL AND A.province IS NOT NULL AND A.city IS NOT NULL; 
q1_1_df = query1_df[]