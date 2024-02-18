import pandas as pd
import time
from sqlalchemy import create_engine


def testQuery(num, star, snowflake):
    base_query = []
    snowflake_query = []
    wrangled_query = []
    index1_query = []
    index2_query = []
    index3_query = []

    connectToDatabase(star, base_query, "mco1datawarehouse")
    connectToDatabase(snowflake, snowflake_query, "mco1datawarehouse2")
    connectToDatabase(star, wrangled_query, "mco1datawarehouse")
    connectToDatabase(star, index1_query, "mco1datawarehouseindex1")
    connectToDatabase(star, index2_query, "mco1datawarehouseindex2")
    connectToDatabase(star, index3_query, "mco1datawarehouseindex3")

    print("QUERY", num, "SUMMARY RESULTS:")
    print("BASE QUERY:", sum(base_query) / len(base_query))
    print("SNOWFLAKE QUERY:", sum(snowflake_query) / len(snowflake_query))
    print("WRANGLED QUERY:", sum(wrangled_query) / len(wrangled_query))
    print("INDEX1 QUERY (MAINSPECIALTY):", sum(index1_query) / len(index1_query))
    print("INDEX2 QUERY (REGION, PROVINCE, CITY):", sum(index2_query) / len(index2_query))
    print("INDEX2 QUERY (TIMEQUEUED):", sum(index3_query) / len(index3_query))



def connectToDatabase(query, time_array, databasename):
    engine = create_engine("mysql://root:Aaron101702@localhost/" + databasename)
    
    for i in range(0, 200):
        with engine.connect() as conn, conn.begin():
                start_time = time.perf_counter() * 100
                pd.read_sql(query, conn)
                end_time = time.perf_counter() * 100

                elapsed_time = end_time  - start_time
                time_array.append(elapsed_time)
                print("Elapsed Time: " + str(elapsed_time))
        
    
#Create charts
######################################################################################################################################
# Chart 1: Get yearly count of appointments, grouped into virtual and non-virtual appointments, for each city (roll-up & drill down) #
######################################################################################################################################

query1 = "SELECT c.region_name, c.province, c.city, YEAR(a.endtime) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus = \"Complete\" AND YEAR(a.endtime) <> 1970 GROUP BY c.region_name, c.province, c.city, YEAR(a.queuedate) WITH ROLLUP ORDER BY c.region_name, c.province, c.city, appointment_year;"
query1_sf = "SELECT l.region_name, l.province, l.city, YEAR(a.endtime) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid JOIN locations l ON c.locationid = l.locationid WHERE a.apptstatus=\"Complete\" AND YEAR(a.endtime) <> 1970 GROUP BY l.region_name, l.province, l.city, YEAR(a.endtime) WITH ROLLUP ORDER BY l.region_name, l.province, l.city, appointment_year;"

query3 = "SELECT DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname, AVG(D.appts) FROM 	(SELECT c.city, c.province, c.region_name, c.hospitalname, DATE(a.queuedate) as apptdate, COUNT(a.apptid) AS appts FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid GROUP BY DATE(a.queuedate), c.region_name, c.province, c.city, c.hospitalname) D GROUP BY DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.region_name, D.province, D.city, D.hospitalname;"
query3_sf = "SELECT DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname, AVG(D.appts) FROM 	(SELECT l.region_name, l.province, l.city, c.hospitalname, DATE(a.queuedate) as apptdate, COUNT(a.apptid) AS appts FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid JOIN locations l ON c.locationid = l.locationid GROUP BY DATE(a.queuedate), l.region_name, l.province, l.city, c.hospitalname) D GROUP BY DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.region_name, D.province, D.city, D.hospitalname;"

query4 = "SELECT d.mainspecialty, a.isvirtual, p.agerange, p.age, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(HOUR, a.timequeued, a.starttime)) AS average_queue_wait_time_hours FROM appointments a JOIN patients p ON a.pxid = p.pxid JOIN doctors d ON a.doctorid = d.doctorid WHERE YEAR(a.starttime) <> 1970 AND p.agerange <> \"INVALID\" AND a.appttype = \"Consultation\" GROUP BY d.mainspecialty, a.isvirtual, p.agerange, p.age WITH ROLLUP ORDER BY d.mainspecialty, a.isvirtual, p.agerange, p.age;"
query4_sf = "SELECT d.mainspecialty, a.isvirtual, p.agerange, p.age, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(HOUR, a.timequeued, a.starttime)) AS average_queue_wait_time_hours FROM appointments a JOIN patients p ON a.pxid = p.pxid JOIN doctors d ON a.doctorid = d.doctorid WHERE YEAR(a.starttime) <> 1970 AND p.agerange <> \"INVALID\" AND a.appttype = \"Consultation\" GROUP BY d.mainspecialty, a.isvirtual, p.agerange, p.age WITH ROLLUP ORDER BY d.mainspecialty, a.isvirtual, p.agerange, p.age;"

testQuery(1, query1, query1_sf)
testQuery(3, query3, query3_sf)
testQuery(4, query4, query4_sf)