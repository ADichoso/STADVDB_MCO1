import pandas as pd
from sqlalchemy import create_engine

#pip install matplotlib
#pip install numpy

def connectToDatabase(query):
    engine = create_engine("mysql://root:Aaron101702@localhost/mco1datawarehouse")
    with engine.connect() as conn, conn.begin():
        return pd.read_sql(query, conn)
    
#Create charts
######################################################################################################################################
# Chart 1: Get yearly count of appointments, grouped into virtual and non-virtual appointments, for each city (roll-up & drill down) #
######################################################################################################################################

query1 = "SELECT c.region_name, c.province, c.city, YEAR(a.queuedate) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus = \"COMPLETE\" AND NOT YEAR(a.queuedate)=1970 GROUP BY c.region_name, c.province, c.city, YEAR(a.queuedate) WITH ROLLUP ORDER BY c.region_name, c.province, c.city, appointment_year;"
query2 = "SELECT d.mainspecialty AS specialty, YEAR(a.starttime) AS appointment_year, MONTH(a.starttime) AS appointment_month, COUNT(*) AS total_appointments FROM appointments a JOIN doctors d ON a.doctorid = d.doctorid WHERE NOT YEAR(a.starttime) = 1970 GROUP BY d.mainspecialty, YEAR(a.starttime), MONTH(a.starttime) WITH ROLLUP ORDER BY d.mainspecialty, YEAR(a.starttime), MONTH(a.starttime);"
query3 = "SELECT DAYOFWEEK(apptdate) AS \"day_of_appointment\", D.city, D.province, D.region_name, AVG(D.appts) FROM (SELECT c.city, c.province, c.region_name, DATE(a.queuedate) as apptdate, COUNT(a.apptid) AS appts FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE YEAR(a.queuedate) <> 1970 GROUP BY DATE(a.queuedate), c.city, c.province, c.region_name) D GROUP BY DAYOFWEEK(apptdate), D.city, D.province, D.region_name WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.city, D.province, D.region_name;"
query4 = "SELECT d.mainspecialty, p.agerange, p.age, a.isvirtual, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(MINUTE, a.starttime, a.endtime)) AS average_appointment_duration_minutes FROM appointments a JOIN patients p ON a.pxid = p.pxid JOIN doctors d ON a.doctorid = d.doctorid WHERE YEAR(a.starttime) <> 1970 AND YEAR(a.endtime) <> 1970 AND a.apptstatus = \"COMPLETE\" AND p.agerange <> \"INVALID\" GROUP BY d.mainspecialty, p.agerange, p.age, a.isvirtual WITH ROLLUP ORDER BY d.mainspecialty, p.agerange, p.age, a.isvirtual;"
query5 = "SELECT c.region_name, c.province, c.city, p.agerange, p.age, d.mainspecialty, COUNT(*) as total_appointments FROM appointments a JOIN patients p ON a.pxid  = p.pxid JOIN  doctors d ON a.doctorid = d.doctorid JOIN clinics c ON a.clinicid = c.clinicid GROUP BY c.region_name, c.province, c.city, p.agerange, p.age, d.mainspecialty  WITH ROLLUP ORDER BY c.region_name, c.province, c.city, p.agerange, p.age, d.mainspecialty;"
query1_df = connectToDatabase(query1)
query2_df = connectToDatabase(query2)
query3_df = connectToDatabase(query3)
query4_df = connectToDatabase(query4)
query5_df = connectToDatabase(query5)
print(query1_df)
print(query2_df)
print(query3_df)
print(query4_df)
print(query5_df)