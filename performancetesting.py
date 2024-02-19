import pandas as pd
import time
from sqlalchemy import create_engine
import sys 

stdoutOrigin=sys.stdout 
sys.stdout = open("log.txt", "w")

def testQuery(num, star, snowflake, refined):
    print("=========QUERY", num, "PERFORMANCE TESTING=========")
    base_query = []
    snowflake_query = []
    refined_query = []
    wrangled_query = []
    index1_query = []
    index2_query = []
    index3_query = []

    print("\n\nBASE QUERY")
    connectToDatabase(star, base_query, "mco1datawarehouse")
    
    print("\n\nSNOWFLAKE QUERY")
    connectToDatabase(snowflake, snowflake_query, "mco1datawarehouse2")
    
    print("\n\REFINED QUERY")
    connectToDatabase(refined, refined_query, "mco1datawarehouse")

    print("\n\nWRANGLED QUERY")
    connectToDatabase(star, wrangled_query, "mco1datawarehouse")
    
    print("\n\nINDEX1 QUERY")
    connectToDatabase(star, index1_query, "mco1datawarehouseindex1")
    
    print("\n\nINDEX2 QUERY")
    connectToDatabase(star, index2_query, "mco1datawarehouseindex2")
    
    print("\n\nINDEX3 QUERY")
    connectToDatabase(star, index3_query, "mco1datawarehouseindex3")

    print("QUERY", num, "SUMMARY RESULTS:")
    print("BASE QUERY:", (sum(base_query) / len(base_query)) * 100, "milliseconds")
    print("SNOWFLAKE QUERY:",(sum(snowflake_query) / len(snowflake_query)) * 100, "milliseconds")
    print("REFINED QUERY:",(sum(refined_query) / len(refined_query)) * 100, "milliseconds")
    print("WRANGLED QUERY:", (sum(wrangled_query) / len(wrangled_query)) * 100, "milliseconds")
    print("INDEX1 QUERY (MAINSPECIALTY):", (sum(index1_query) / len(index1_query)) * 100, "milliseconds")
    print("INDEX2 QUERY (REGION, PROVINCE, CITY):", (sum(index2_query) / len(index2_query)) * 100, "milliseconds")
    print("INDEX2 QUERY (TIMEQUEUED):", (sum(index3_query) / len(index2_query)) * 100, "milliseconds")



def connectToDatabase(query, time_array, databasename):
    engine = create_engine("mysql://root:Aaron101702@localhost/" + databasename)
    
    for i in range(0, 50):
        with engine.connect() as conn, conn.begin():
                start_time = time.perf_counter()
                pd.read_sql(query, conn)
                end_time = time.perf_counter()

                elapsed_time = end_time  - start_time
                time_array.append(elapsed_time)
                print(str(elapsed_time), end=",")
        
    
#Create charts
######################################################################################################################################
# Chart 1: Get yearly count of appointments, grouped into virtual and non-virtual appointments, for each city (roll-up & drill down) #
######################################################################################################################################

query1 = "SELECT c.region_name, c.province, c.city, YEAR(a.endtime) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus = \"Complete\" AND YEAR(a.endtime) <> 1970 GROUP BY c.region_name, c.province, c.city, YEAR(a.endtime) WITH ROLLUP ORDER BY c.region_name, c.province, c.city, appointment_year;"
query1_sf = "SELECT l.region_name, l.province, l.city, YEAR(a.endtime) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid JOIN locations l ON c.locationid = l.locationid WHERE a.apptstatus=\"Complete\" AND YEAR(a.endtime) <> 1970 GROUP BY l.region_name, l.province, l.city, YEAR(a.endtime) WITH ROLLUP ORDER BY l.region_name, l.province, l.city, appointment_year;"
query1_rf = "SELECT c.region_name, c.province, c.city, YEAR(a.endtime) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM (SELECT clinicid, endtime, isvirtual FROM appointments WHERE apptstatus=\"Complete\" AND YEAR(endtime) <> 1970) a JOIN clinics c ON a.clinicid = c.clinicid GROUP BY c.region_name, c.province, c.city, YEAR(a.endtime) WITH ROLLUP ORDER BY c.region_name, c.province, c.city, appointment_year;"

query3 = "SELECT DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname, AVG(D.appts) FROM 	(SELECT c.city, c.province, c.region_name, c.hospitalname, DATE(a.queuedate) as apptdate, COUNT(a.apptid) AS appts FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus = \"Complete\" OR a.apptstatus = \"Queued\" OR a.apptstatus = \"Serving\" GROUP BY DATE(a.queuedate), c.region_name, c.province, c.city, c.hospitalname) D GROUP BY DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.region_name, D.province, D.city, D.hospitalname;"
query3_sf = "SELECT DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname, AVG(D.appts) FROM 	(SELECT l.region_name, l.province, l.city, c.hospitalname, DATE(a.queuedate) as apptdate, COUNT(a.apptid) AS appts FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid JOIN locations l ON c.locationid = l.locationid WHERE a.apptstatus = \"Complete\" OR a.apptstatus = \"Queued\" OR a.apptstatus = \"Serving\" GROUP BY DATE(a.queuedate), l.region_name, l.province, l.city, c.hospitalname) D GROUP BY DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.region_name, D.province, D.city, D.hospitalname;"
query3_rf = "SELECT DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname, AVG(D.appts) FROM (SELECT c.city, c.province, c.region_name, c.hospitalname, DATE(a.queuedate) as apptdate, COUNT(*) AS appts FROM (SELECT clinicid, queuedate FROM appointments WHERE apptstatus = \"Complete\" OR apptstatus = \"Queued\" OR apptstatus = \"Serving\") a JOIN clinics c ON a.clinicid = c.clinicid GROUP BY DATE(a.queuedate), c.region_name, c.province, c.city, c.hospitalname) D GROUP BY DAYOFWEEK(apptdate), D.region_name, D.province, D.city, D.hospitalname WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.region_name, D.province, D.city, D.hospitalname;"

query4 = "SELECT d.mainspecialty, a.isvirtual, p.agerange, p.age, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(HOUR, a.timequeued, a.starttime)) AS average_queue_wait_time_hours FROM appointments a JOIN patients p ON a.pxid = p.pxid JOIN doctors d ON a.doctorid = d.doctorid WHERE YEAR(a.starttime) <> 1970 AND p.agerange <> \"INVALID\" AND a.appttype = \"Consultation\" GROUP BY d.mainspecialty, a.isvirtual, p.agerange, p.age WITH ROLLUP ORDER BY d.mainspecialty, a.isvirtual, p.agerange, p.age;"
query4_sf = "SELECT d.mainspecialty, a.isvirtual, p.agerange, p.age, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(HOUR, a.timequeued, a.starttime)) AS average_queue_wait_time_hours FROM appointments a JOIN patients p ON a.pxid = p.pxid JOIN doctors d ON a.doctorid = d.doctorid WHERE YEAR(a.starttime) <> 1970 AND p.agerange <> \"INVALID\" AND a.appttype = \"Consultation\" GROUP BY d.mainspecialty, a.isvirtual, p.agerange, p.age WITH ROLLUP ORDER BY d.mainspecialty, a.isvirtual, p.agerange, p.age;"
query4_rf = "SELECT d.mainspecialty, a.isvirtual, p.agerange, p.age, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(HOUR, timequeued, starttime)) AS average_queue_wait_time_hours FROM doctors d JOIN (SELECT doctorid, pxid, apptid, isvirtual, timequeued, starttime FROM appointments WHERE YEAR(starttime) <> 1970 AND appttype = \"Consultation\") a ON d.doctorid = a.doctorid JOIN (SELECT pxid, agerange, age FROM patients WHERE agerange <> \"INVALID\") p ON p.pxid = a.pxid GROUP BY d.mainspecialty, a.isvirtual, p.agerange, p.age WITH ROLLUP ORDER BY d.mainspecialty, a.isvirtual, p.agerange, p.age;"

testQuery(1, query1, query1_sf, query1_rf)
testQuery(3, query3, query3_sf, query3_rf)
testQuery(4, query4, query4_sf, query4_rf)

sys.stdout.close()
sys.stdout=stdoutOrigin