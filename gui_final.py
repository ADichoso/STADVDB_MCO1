_DEBUG = True #skip connecting to the database

import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd
from sqlalchemy import create_engine

#pip install matplotlib
#pip install numpy

def connectToDatabase(query):
    config = {
    'user': 'root',
    'password': 'admin',
    'host': 'localhost',
    'database': 'mco1datawarehouse',
    'raise_on_warnings': True
    }

    engine = create_engine("mysql://root:admin@localhost/mco1datawarehouse")
    with engine.connect() as conn, conn.begin():
        return pd.read_sql(query, conn)
    
#Create charts
if (_DEBUG):
    query1 = "SELECT c.region_name, c.province, c.city, YEAR(a.queuedate) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus = \"COMPLETE\" AND NOT YEAR(a.queuedate)=1970 GROUP BY c.region_name, c.province, c.city, YEAR(a.queuedate) WITH ROLLUP ORDER BY c.region_name, c.province, c.city, appointment_year;"
    query3 = "SELECT DAYOFWEEK(apptdate) AS \"day_of_appointment\", D.city, D.province, D.region_name, AVG(D.appts) FROM (SELECT c.city, c.province, c.region_name, DATE(a.queuedate) as apptdate, COUNT(a.apptid) AS appts FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE YEAR(a.queuedate) <> 1970 GROUP BY DATE(a.queuedate), c.city, c.province, c.region_name) D GROUP BY DAYOFWEEK(apptdate), D.city, D.province, D.region_name WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.city, D.province, D.region_name;"
    query4 = "SELECT d.mainspecialty, p.agerange, p.age, a.isvirtual, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(MINUTE, a.starttime, a.endtime)) AS average_appointment_duration_minutes FROM appointments a JOIN patients p ON a.pxid = p.pxid JOIN doctors d ON a.doctorid = d.doctorid WHERE YEAR(a.starttime) <> 1970 AND YEAR(a.endtime) <> 1970 AND a.apptstatus = \"COMPLETE\" AND p.agerange <> \"INVALID\" GROUP BY d.mainspecialty, p.agerange, p.age, a.isvirtual WITH ROLLUP ORDER BY d.mainspecialty, p.agerange, p.age, a.isvirtual;"
    query1_df = connectToDatabase(query1)
    query3_df = connectToDatabase(query3)
    query4_df = connectToDatabase(query4)
    print(query1_df)
    print(query3_df)
    print(query4_df)

############
# Chart 1: # Yearly virtual and non-virtual appointments by province
############
q1_1_df = query1_df.loc[query1_df['region_name'].notnull() & query1_df['province'].notnull() & query1_df['city'].isnull() & query1_df['appointment_year'].isnull()]

##############
# Chart 1_1: # slice only look at 1 specific year (showing appointments for each city in the year 2020) 
##############
q1_slice_df = query1_df.loc[query1_df['region_name'].notnull() & query1_df['province'].notnull() & query1_df['city'].notnull()]
q1_slice_df = q1_slice_df.loc[query1_df['appointment_year'] == 2020]

##############
# Chart 1_2: # dice Yearly count of appointments from 2020-2021, for National Capital Region (NCR) and CALABARZON (IV-A)
##############
q1_dice_df = query1_df.loc[query1_df['province'].notnull() & query1_df['city'].notnull()]
q1_dice_df = q1_dice_df.loc[(query1_df['region_name'] == 'National Capital Region (NCR)') | (query1_df['region_name'] == 'CALABARZON (IV-A)')]
q1_dice_df = q1_dice_df.loc[(query1_df['appointment_year'] == 2020) | (query1_df['appointment_year'] == 2021)]

##############
# Chart 1_3: # drilldown Yearly virtual and non-virtual appointments by city
##############
q1_drilldown_df = query1_df.loc[query1_df['region_name'].notnull() & query1_df['province'].notnull() & query1_df['city'].notnull() & query1_df['appointment_year'].isnull()]

##############
# Chart 1_4: # roll up drilldown Yearly virtual and non-virtual appointments by region
##############   
q1_rollup_df = query1_df.loc[query1_df['region_name'].notnull() & query1_df['province'].isnull() & query1_df['city'].isnull() & query1_df['appointment_year'].isnull()]

############
# Chart 3: # average appointments per day of the week in each province
############
q3_1_df = query3_df.loc[query3_df['appt_day_of_week'].notnull() & query3_df['region_name'].notnull() & query3_df['province'].notnull() & query3_df['city'].isnull()]

##############
# Chart 3_1: # slice refine to show the average number of appointments on monday
##############
q3_slice_df = query3_df.loc[(query3_df['appt_day_of_week'] == 1) & query3_df['region_name'].notnull() & query3_df['province'].notnull() & query3_df['city'].notnull()]

##############
# Chart 3_2: # dice refine to show the average number of appointments in laguna and manila on weekends
##############
q3_dice_df = query3_df.loc[query3_df['region_name'].notnull() & query3_df['city'].notnull()]
q3_dice_df = q3_dice_df.loc[(query3_df['province'] == 'Laguna') | (query3_df['province'] == 'Manila')]
q3_dice_df = q3_dice_df.loc[(query3_df['appt_day_of_week'] == 6) | (query3_df['appt_day_of_week'] == 7)]

##############
# Chart 3_3: # drill down average appointments per day of the week in each city
##############
q3_drilldown_df = query3_df.loc[query3_df['appt_day_of_week'].notnull() & query3_df['region_name'].notnull() & query3_df['province'].notnull() & query3_df['city'].notnull()]

##############
# Chart 3_4: # roll up average appointments per day of the week in each region
##############
q3_rollup_df = query3_df.loc[query3_df['appt_day_of_week'].notnull() & query3_df['region_name'].notnull() & query3_df['province'].isnull() & query3_df['city'].isnull()]

############
# Chart 4: #  from the average appointment duration per doctor specialty
############
q4_1_df = query4_df.loc[query4_df['mainspecialty'].notnull() & query4_df['isvirtual'].notnull() & query4_df['agerange'].isnull() & query4_df['age'].isnull()]

##############
# Chart 4_1: # slice show the count of appointments per age range and doctor specialty for virtual appointments
##############
q4_slice_df = query4_df.loc[query4_df['mainspecialty'].notnull() & (query4_df['isvirtual'] == 1) & query4_df['agerange'].notnull() & query4_df['age'].isnull()]

##############
# Chart 4_2: # dice show the count of appointments per age range and doctor specialty for virtual appointments that lasted longer than a certain threshold duration
##############
q4_dice_df = query4_df.loc[query4_df['mainspecialty'].notnull() & query4_df['isvirtual'].notnull() & query4_df['agerange'].notnull() & query4_df['age'].isnull()]
q4_dice_df = q4_dice_df.loc[query4_df['average_queue_wait_time_hours'] > 24]

##############
# Chart 4_3: # drill down average appointment duration per age range within each specialty 
##############
q4_drilldown_df = query4_df.loc[query4_df['mainspecialty'].notnull() & query4_df['isvirtual'].notnull() & query4_df['agerange'].notnull() & query4_df['age'].isnull()]

##############
# Chart 4_4: # roll up see the overall average appointment duration per specialty
##############
q4_rollup_df = query4_df.loc[query4_df['mainspecialty'].notnull() & query4_df['isvirtual'].isnull() & query4_df['agerange'].isnull() & query4_df['age'].isnull()]

#place all figures in this list
'''
figure_list = [
    [fig1, fig1_1, fig1_2, fig1_3, fig1_4],
    [fig2, fig2_1, fig2_2, fig2_3],
    [fig3, fig3_1, fig3_2], 
    [fig4_1, fig4_1_1]
]

df_list = [
    [query1_df, query1_1_df, query1_2_df, query1_3_df, query1_4_df],
    [query2_df, query2_1_df, query2_2_df, query2_3_df],
    [query3_df, query3_1_df, query3_2_df], 
    [query4_df, query4_1_df, df4_1_1]
]
'''
#GUI
root = tk.Tk()
root.title('OLAP Application')
root.geometry("800x450")
root.pack_propagate(0)

main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=1)

main_canvas = tk.Canvas(main_frame)
main_canvas.pack(side="right", fill="both", expand=1)

side_frame = tk.Frame(main_frame, padx=5, pady=5)
side_frame.pack(side="left", padx=5,pady=5, fill="y")

scrollbar = tk.Scrollbar(main_frame, orient='vertical', command=main_canvas.yview)
scrollbar.pack(side="right", fill='y')

main_canvas.configure(yscrollcommand=scrollbar.set)
main_canvas.bind('<Configure>', lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all")))

second_frame = tk.Frame(main_canvas)
canvas1 = FigureCanvasTkAgg(fig1, second_frame)
canvas2 = tk.Frame(second_frame, padx=5, pady=5)
canvas2.pack(side="left", padx=5,pady=5, fill="y")

main_canvas.create_window((0,0), window=second_frame, anchor="nw")

def button_update(image_number, refinement_number, view_type):
    global canvas1
    global canvas2
    global side_frame
    global main_canvas
    global scrollbar

    image_number = image_number % len(figure_list)
    
    for child in side_frame.winfo_children():
        child.destroy()

    for child in canvas2.winfo_children():
        child.destroy()
    
    canvas2.pack_forget()
    canvas2 = tk.Frame(second_frame, padx=5, pady=5)
    canvas2.pack(side="left", padx=5,pady=5, fill="y")

    canvas1.get_tk_widget().pack_forget()
    
    if view_type:
        curr_df = df_list[image_number][refinement_number]
        for j in range(len(curr_df.columns)):
            tk.Label(text=curr_df.columns[j].replace('_', ' ').title(), master=canvas2, font='Helvetica 10 bold').grid(row=0,column=j, sticky="W", padx=10, pady=5)
            
            for i in range(len(curr_df)):
                tk.Label(text=curr_df.iloc[i,j], master=canvas2).grid(row=i+1,column=j, sticky="W", padx=10)
    else:
        canvas1 = FigureCanvasTkAgg(figure_list[image_number][refinement_number], second_frame)
        canvas1.draw()
        canvas1.get_tk_widget().pack(side="left")
        
    
    button_back = tk.Button(side_frame, text = "<<", command=lambda: button_update(image_number-1, 0, view_type), width=5)
    curr_fig = tk.Label(text="Fig: "+str(image_number+1), master=side_frame, width=5, pady=20)
    curr_ref = tk.Label(text="Ref: "+chr(ord('`')+refinement_number+1), master=side_frame, width=5)
    button_next = tk.Button(side_frame, text = ">>", command=lambda: button_update(image_number+1, 0, view_type), width=5)
    table_view = tk.Button(side_frame, text = "<o>", command=lambda: button_update(image_number, 0, not view_type), width=5)

    table_view.grid(row=1,column=0)
    button_back.grid(row=0, column=0)
    curr_fig.grid(row=0, column=1)
    curr_ref.grid(row=1, column=1)
    button_next.grid(row=0, column=2)

    for i in range(len(figure_list[image_number])):
        tk.Button(side_frame, text = chr(ord('`')+i+1), command=lambda i=i: button_update(image_number, i, view_type), width=8).grid(row=i+2,column=1, pady=2)

    main_canvas.yview_moveto(0)
    main_canvas.update_idletasks()
    main_canvas.configure(scrollregion=main_canvas.bbox("all"))
    

button_update(0, 0, False)
root.mainloop()