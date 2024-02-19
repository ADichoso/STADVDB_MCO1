import pandas as pd
import time
from sqlalchemy import create_engine
import sys 

stdoutOrigin=sys.stdout 
sys.stdout = open("log.txt", "w")

def testQuery(num, star):
    print("=========QUERY", num, "PERFORMANCE TESTING=========")
    device2_query = []

    print("\n\DEVICE 2 QUERY")
    connectToDatabase(star, device2_query, "mco1datawarehouse")

    print("QUERY", num, "SUMMARY RESULTS:")
    print("DEVICE 2 QUERY:", (sum(device2_query) / len(device2_query)) * 100, "milliseconds")

def connectToDatabase(query, time_array, databasename):
    engine = create_engine("mysql://root:Aaron101702@localhost/" + databasename)
    
    for i in range(0, 50):
        with engine.connect() as conn, conn.begin():
                start_time = time.perf_counter()
                pd.read_sql(query, conn)
                end_time = time.perf_counter()

                elapsed_time = end_time  - start_time
                time_array.append(elapsed_time)
                print("Elapsed Time: " + str(elapsed_time))
        
    
#Create charts
######################################################################################################################################
# Chart 1: Get yearly count of appointments, grouped into virtual and non-virtual appointments, for each city (roll-up & drill down) #
######################################################################################################################################

query1 = "SELECT c.region_name, c.province, c.city, YEAR(a.endtime) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus = \"Complete\" AND YEAR(a.endtime) <> 1970 GROUP BY c.region_name, c.province, c.city, YEAR(a.endtime) WITH ROLLUP ORDER BY c.region_name, c.province, c.city, appointment_year;"
query3 = "SELECT DAYOFWEEK(apptdate), D.region_name, D.province, D.city, AVG(D.appts) FROM 	(SELECT c.city, c.province, c.region_name, DATE(a.queuedate) as apptdate, COUNT(a.apptid) AS appts FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus = \"Complete\" OR a.apptstatus = \"Queued\" OR a.apptstatus = \"Serving\" GROUP BY DATE(a.queuedate), c.region_name, c.province, c.city) D GROUP BY DAYOFWEEK(apptdate), D.region_name, D.province, D.city WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.region_name, D.province, D.city;"
query4 = "SELECT d.mainspecialty, a.isvirtual, p.agerange, p.age, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(HOUR, a.timequeued, a.starttime)) AS average_queue_wait_time_hours FROM appointments a JOIN patients p ON a.pxid = p.pxid JOIN doctors d ON a.doctorid = d.doctorid WHERE YEAR(a.starttime) <> 1970 AND p.agerange <> \"INVALID\" AND a.appttype = \"Consultation\" GROUP BY d.mainspecialty, a.isvirtual, p.agerange, p.age WITH ROLLUP ORDER BY d.mainspecialty, a.isvirtual, p.agerange, p.age;"

testQuery(1, query1)
testQuery(3, query3)
testQuery(4, query4)

sys.stdout.close()
sys.stdout=stdoutOrigin