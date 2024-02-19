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
    query1 = "SELECT c.region_name, c.province, c.city, YEAR(a.endtime) AS appointment_year, SUM(CASE WHEN a.isvirtual = 1 THEN 1 ELSE 0 END) AS virtual_appointments, SUM(CASE WHEN a.isvirtual = 0 THEN 1 ELSE 0 END) AS non_virtual_appointments FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus=\"Complete\" AND YEAR(a.endtime) <> 1970 GROUP BY c.region_name, c.province, c.city, YEAR(a.endtime) WITH ROLLUP ORDER BY c.region_name, c.province, c.city, appointment_year"
    query3 = "SELECT DAYOFWEEK(apptdate) as appt_day_of_week, D.region_name, D.province, D.city, AVG(D.appts) FROM 	(SELECT c.city, c.province, c.region_name, DATE(a.queuedate) as apptdate, COUNT(*) AS appts FROM appointments a JOIN clinics c ON a.clinicid = c.clinicid WHERE a.apptstatus = \"Complete\" OR a.apptstatus = \"Queued\" OR a.apptstatus = \"Serving\" GROUP BY DATE(a.queuedate), c.region_name, c.province, c.city) D GROUP BY DAYOFWEEK(apptdate), D.region_name, D.province, D.city WITH ROLLUP ORDER BY DAYOFWEEK(apptdate), AVG(D.appts) DESC, D.region_name, D.province, D.city"
    query4 = "SELECT d.mainspecialty, a.isvirtual, p.agerange, p.age, COUNT(a.apptid) AS count_appointments, AVG(TIMESTAMPDIFF(HOUR, a.timequeued, a.starttime)) AS average_queue_wait_time_hours FROM appointments a JOIN patients p ON a.pxid = p.pxid JOIN doctors d ON a.doctorid = d.doctorid WHERE YEAR(a.starttime) <> 1970 AND p.agerange <> \"INVALID\" AND a.appttype = \"Consultation\" GROUP BY d.mainspecialty, a.isvirtual, p.agerange, p.age WITH ROLLUP ORDER BY d.mainspecialty, a.isvirtual, p.agerange, p.age"   
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
fig1, ax1 = plt.subplots(figsize=(11, 10))
num_provinces = len(q1_1_df['province'])
bar_width = 0.35
positions = range(num_provinces)
ax1.bar(positions, q1_1_df['virtual_appointments'], width=bar_width, label='Virtual Appointments')
ax1.bar([pos + bar_width for pos in positions], q1_1_df['non_virtual_appointments'], width=bar_width, label='Non-virtual Appointments')
ax1.set_xlabel('Province')
ax1.set_ylabel('Number of Appointments')
ax1.set_title('Yearly Virtual and Non-virtual Appointments by Province')
ax1.legend()
ax1.set_xticks([pos + bar_width / 2 for pos in positions])
ax1.set_xticklabels(q1_1_df['province'], rotation=45, fontsize=8)
plt.tight_layout()

##############
# Chart 1_1: # slice only look at 1 specific year (showing appointments for each city in the year 2020) 
##############
fig1_1, ax1_1 = plt.subplots(figsize=(11, 10))
q1_slice_df = query1_df.loc[query1_df['region_name'].notnull() & query1_df['province'].notnull() & query1_df['city'].notnull()]
q1_slice_df = query1_df.loc[query1_df['appointment_year'] == 2020]
q1_slice_df.drop(columns='appointment_year').plot(kind='bar', ax=ax1_1)
ax1_1.set_title('Appointment Counts by City in 2020')
ax1_1.set_xlabel('City')
ax1_1.set_ylabel('Appointment Count')
city_names = q1_slice_df['city'].tolist()
ax1_1.set_xticklabels(city_names, rotation=45, fontsize=8)
plt.tight_layout()


##############
# Chart 1_2: # dice Yearly count of appointments from 2020-2021, for National Capital Region (NCR) and CALABARZON (IV-A)
##############
q1_dice_df = query1_df.loc[query1_df['province'].notnull() & query1_df['city'].notnull()]
q1_dice_df = q1_dice_df.loc[(query1_df['region_name'] == 'National Capital Region (NCR)') | (query1_df['region_name'] == 'CALABARZON (IV-A)')]
q1_dice_df = q1_dice_df.loc[(query1_df['appointment_year'] == 2020) | (query1_df['appointment_year'] == 2021)]
grouped_df = q1_dice_df.groupby(['region_name', 'appointment_year']).size().unstack()
fig1_2, ax1_2 = plt.subplots(figsize=(10, 6))
num_regions = len(grouped_df)
bar_width = 0.35 
bar_positions1 = range(num_regions)
bars1 = ax1_2.bar(bar_positions1, grouped_df.loc['National Capital Region (NCR)'], width=bar_width, label='NCR')
bar_positions2 = [pos + bar_width for pos in bar_positions1]
bars2 = ax1_2.bar(bar_positions2, grouped_df.loc['CALABARZON (IV-A)'], width=bar_width, label='CALABARZON')
ax1_2.set_title('Yearly Count of Appointments (2020-2021)')
ax1_2.set_xlabel('Year')
ax1_2.set_ylabel('Number of Appointments')
ax1_2.set_xticks([pos + bar_width / 2 for pos in bar_positions1])
ax1_2.set_xticklabels(grouped_df.columns)  
ax1_2.legend()
plt.tight_layout()

##############
# Chart 1_3: # drilldown Yearly virtual and non-virtual appointments by city
##############
q1_drilldown_df = query1_df.loc[query1_df['region_name'].notnull() & query1_df['province'].notnull() & query1_df['city'].notnull() & query1_df['appointment_year'].isnull()]

#q1_drilldown_df = query1_df.loc[query1_df['region_name'].notnull() & query1_df['province'].notnull() & query1_df['city'].notnull() & query1_df['appointment_year'].notnull()]
num_cities = len(q1_drilldown_df['city'])
bar_width = 0.35
positions = range(num_cities)
fig1_3, ax1_3 = plt.subplots(figsize=(11, 10))
ax1_3 .bar(positions, q1_drilldown_df['virtual_appointments'], width=bar_width, label='Virtual Appointments')
ax1_3 .bar([pos + bar_width for pos in positions], q1_drilldown_df['non_virtual_appointments'], width=bar_width, label='Non-virtual Appointments')
ax1_3 .set_xlabel('City')
ax1_3 .set_ylabel('Number of Appointments')
ax1_3 .set_title('Yearly Virtual and Non-virtual Appointments by City')
ax1_3 .legend()
ax1_3 .set_xticks([pos + bar_width / 2 for pos in positions])
ax1_3 .set_xticklabels(q1_drilldown_df['city'], rotation=45, fontsize=8)
plt.tight_layout()

##############
# Chart 1_4: # roll up Yearly virtual and non-virtual appointments by region
##############   
q1_rollup_df = query1_df.loc[query1_df['region_name'].notnull() & query1_df['province'].isnull() & query1_df['city'].isnull() & query1_df['appointment_year'].isnull()]
num_regions = len(q1_rollup_df['region_name'])
bar_width = 0.35
positions = range(num_regions)
fig1_4, ax1_4 = plt.subplots(figsize=(11, 10))
ax1_4.bar(positions, q1_rollup_df['virtual_appointments'], width=bar_width, label='Virtual Appointments')
ax1_4.bar([pos + bar_width for pos in positions], q1_rollup_df['non_virtual_appointments'], width=bar_width, label='Non-virtual Appointments')
ax1_4.set_xlabel('Region')
ax1_4.set_ylabel('Number of Appointments')
ax1_4.set_title('Yearly Virtual and Non-virtual Appointments by Region')
ax1_4.legend()
ax1_4.set_xticks([pos + bar_width / 2 for pos in positions])
ax1_4.set_xticklabels(q1_rollup_df['region_name'], rotation=45, fontsize=8)
plt.tight_layout()

############
# Chart 3: # average appointments per day of the week in each province
############
q3_1_df = query3_df.loc[query3_df['appt_day_of_week'].notnull() & query3_df['region_name'].notnull() & query3_df['province'].notnull() & query3_df['city'].isnull()]
q3_1_grouped_df = q3_1_df.groupby(['province', 'appt_day_of_week'])['AVG(D.appts)'].mean().reset_index()
pivot_df = q3_1_grouped_df.pivot(index='province', columns='appt_day_of_week', values='AVG(D.appts)')
fig3, ax3 = plt.subplots(figsize=(10, 6))
pivot_df.plot(kind='bar', ax=ax3)
ax3.set_title('Average Appointments per Day of the Week in Each Province')
ax3.set_xlabel('Province')
ax3.set_ylabel('Average Appointments')
ax3.set_xticklabels(pivot_df.index, rotation=45, ha='right', fontsize=8)
ax3.legend(title='Day of the Week', labels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.tight_layout()


##############
# Chart 3_1: # slice refine to show the average number of appointments on monday
##############
q3_slice_df = query3_df.loc[(query3_df['appt_day_of_week'] == 1) & query3_df['region_name'].notnull() & query3_df['province'].notnull() & query3_df['city'].notnull()]
avg_appointments_per_region = q3_slice_df.groupby('region_name')['AVG(D.appts)'].mean()
fig3_1, ax3_1 = plt.subplots(figsize=(10, 9))
avg_appointments_per_region.plot(kind='bar', ax=ax3_1, color='skyblue')
ax3_1.set_title('Average Number of Appointments on Monday by Region')
ax3_1.set_xlabel('Region')
ax3_1.set_ylabel('Average Number of Appointments')
ax3_1.set_xticklabels(avg_appointments_per_region.index, rotation=45, ha='right', fontsize=5)


##############
# Chart 3_2: # dice refine to show the average number of appointments in laguna and manila on weekends
##############
q3_dice_df = query3_df.loc[query3_df['region_name'].notnull() & query3_df['city'].notnull()]
q3_dice_df = q3_dice_df.loc[(query3_df['province'] == 'Laguna') | (query3_df['province'] == 'Manila')]
q3_dice_df = q3_dice_df.loc[(query3_df['appt_day_of_week'] == 6) | (query3_df['appt_day_of_week'] == 7)]
avg_appointments_per_province = q3_dice_df.groupby('province')['AVG(D.appts)'].mean()
fig3_2, ax3_2 = plt.subplots(figsize=(10, 8))
avg_appointments_per_province.plot(kind='bar', ax=ax3_2, color='skyblue')
ax3_2.set_title('Average Number of Appointments in Laguna and Manila on Weekends')
ax3_2.set_ylabel('Average Number of Appointments')
ax3_2.set_xlabel('Province')
ax3_2.set_xticklabels(avg_appointments_per_province.index, rotation=45, ha='right', fontsize=10)

##############
# Chart 3_3: # drill down average appointments per day of the week in each city
##############
q3_drilldown_df = query3_df.loc[query3_df['appt_day_of_week'].notnull() & query3_df['region_name'].notnull() & query3_df['province'].notnull() & query3_df['city'].notnull()]
q3_drilldown_grouped_df = q3_drilldown_df.groupby(['city', 'appt_day_of_week'])['AVG(D.appts)'].mean().reset_index()
pivot_drilldown_df = q3_drilldown_grouped_df.pivot(index='city', columns='appt_day_of_week', values='AVG(D.appts)')
fig3_3, ax3_3 = plt.subplots(figsize=(10, 6))
pivot_drilldown_df.plot(kind='bar', ax=ax3_3)
ax3_3.set_title('Average Appointments per Day of the Week in Each City')
ax3_3.set_xlabel('City')
ax3_3.set_ylabel('Average Appointments')
ax3_3.set_xticklabels(pivot_drilldown_df.index, rotation=45, ha='right', fontsize=8)
ax3_3.legend(title='Day of the Week', labels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.tight_layout()

##############
# Chart 3_4: # roll up average appointments per day of the week in each region
##############
q3_rollup_df = query3_df.loc[query3_df['appt_day_of_week'].notnull() & query3_df['region_name'].notnull() & query3_df['province'].isnull() & query3_df['city'].isnull()]
q3_rollup_grouped_df = q3_rollup_df.groupby(['region_name', 'appt_day_of_week'])['AVG(D.appts)'].mean().reset_index()
pivot_rollup_df = q3_rollup_grouped_df.pivot(index='region_name', columns='appt_day_of_week', values='AVG(D.appts)')
fig3_4, ax3_4 = plt.subplots(figsize=(10, 6))
pivot_rollup_df.plot(kind='bar', ax=ax3_4)
ax3_4.set_title('Average Appointments per Day of the Week in Each Region')
ax3_4.set_xlabel('Region')
ax3_4.set_ylabel('Average Appointments')
ax3_4.set_xticklabels(pivot_rollup_df.index, rotation=45, ha='right', fontsize=8)
ax3_4.legend(title='Day of the Week', labels=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
plt.tight_layout()

############
# Chart 4: #  from the average appointment duration per doctor specialty
############
q4_1_df = query4_df.loc[query4_df['mainspecialty'].notnull() & query4_df['isvirtual'].notnull() & query4_df['agerange'].isnull() & query4_df['age'].isnull()]
q4_df_top10 = q4_1_df.nlargest(30, 'average_queue_wait_time_hours')
fig4, ax4 = plt.subplots(figsize=(11, 10))
q4_df_top10.plot(kind='bar', x='mainspecialty', y='average_queue_wait_time_hours', ax=ax4, color='skyblue')
ax4.set_title('Average Queue Wait Time per Doctor Specialty for Virtual Appointments')
ax4.set_xlabel('Doctor Specialty')
ax4.set_ylabel('Average Queue Wait Time (hours)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

##############
# Chart 4_1: # slice show the count of appointments per age range and doctor specialty for virtual appointments
##############
q4_slice_df = query4_df.loc[query4_df['mainspecialty'].notnull() & (query4_df['isvirtual'] == 1) & query4_df['agerange'].notnull() & query4_df['age'].isnull()]
query4_1_df = query4_df.loc[
    query4_df['mainspecialty'].notnull() &
    query4_df['isvirtual'].notnull() &
    query4_df['agerange'].isnull() &  
    query4_df['age'].isnull()          
]
fig4_1, ax4_1 = plt.subplots(figsize=(10, 6))
query4_1_df['isvirtual'] = query4_1_df['isvirtual'].astype(bool)
query4_1_df['mainspecialty'] = query4_1_df['mainspecialty'].astype('category')
query4_1_df['agerange'] = query4_1_df['agerange'].astype('category')
query4_1_df.pivot(index='mainspecialty', columns='isvirtual', values='count_appointments').plot(kind='bar', ax=ax4_1)
ax4_1.set_title('Count of Appointments per Age Range and Doctor Specialty for Virtual Appointments')
ax4_1.set_xlabel('Specialty')
ax4_1.set_ylabel('Count of Appointments')
ax4_1.legend(labels=['Virtual Appointments', 'Non-Virtual Appointments'])
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

##############
# Chart 4_2: # dice show the count of appointments per age range and doctor specialty for virtual appointments that lasted longer than a certain threshold duration
##############
q4_dice_df = query4_df.loc[query4_df['mainspecialty'].notnull() & query4_df['isvirtual'].notnull() & query4_df['agerange'].notnull() & query4_df['age'].isnull()]
q4_dice_df = q4_dice_df.loc[query4_df['average_queue_wait_time_hours'] > 24]
query4_2_df = query4_df.loc[
    query4_df['mainspecialty'].notnull() &
    query4_df['isvirtual'].notnull() &
    query4_df['agerange'].notnull() &
    query4_df['age'].isnull() &
    (query4_df['average_queue_wait_time_hours'] > 24)
]
fig4_2, ax4_2 = plt.subplots(figsize=(10, 6))
aggregated_df = query4_2_df.groupby(['mainspecialty', 'agerange'])['count_appointments'].sum().reset_index()
aggregated_df.pivot(index='mainspecialty', columns='agerange', values='count_appointments').plot(kind='bar', ax=ax4_2)
ax4_2.set_title('Count of Appointments per Age Range and Doctor Specialty for Virtual Appointments (Duration > 24 minutes)')
ax4_2.set_xlabel('Specialty')
ax4_2.set_ylabel('Count of Appointments')
plt.xticks(rotation=45, ha='right')  # Rotate x-axis labels for better readability
plt.tight_layout()

##############
# Chart 4_3: # drill down average appointment duration per age range within each specialty 
##############
q4_drilldown_df = query4_df.loc[query4_df['mainspecialty'].notnull() & query4_df['isvirtual'].notnull() & query4_df['agerange'].notnull() & query4_df['age'].isnull()]

query4_3_df = query4_df.loc[
    query4_df['mainspecialty'].notnull() &
    query4_df['isvirtual'].notnull() &
    query4_df['agerange'].notnull() &
    query4_df['age'].isnull()
]
grouped_df = query4_3_df.groupby(['mainspecialty', 'agerange'])['average_queue_wait_time_hours'].mean().reset_index()
grouped_df.set_index(['mainspecialty', 'agerange'], inplace=True)
fig4_3, ax4_3 = plt.subplots(figsize=(12, 11))
grouped_df.plot(kind='bar', ax=ax4_3)
ax4_3.set_title('Average Appointment Duration per Age Range Within Each Specialty')
ax4_3.set_xlabel('Specialty - Age Range')
ax4_3.set_ylabel('Average Appointment Duration (minutes)')
ax4_3.legend(labels=['Avg queue wait time'])
plt.xticks(rotation=45, ha='right')
plt.tight_layout()


##############
# Chart 4_4: # roll up see the overall average appointment duration per specialty
##############
q4_rollup_df = query4_df.loc[query4_df['mainspecialty'].notnull() & query4_df['isvirtual'].isnull() & query4_df['agerange'].isnull() & query4_df['age'].isnull()]
query4_4_df = query4_df.loc[query4_df['mainspecialty'].notnull() & query4_df['isvirtual'].isnull() & query4_df['agerange'].isnull() & query4_df['age'].isnull()]
fig4_4, ax4_4 = plt.subplots(figsize=(10, 6))
query4_4_df.plot(kind='bar', x='mainspecialty', y='average_queue_wait_time_hours', ax=ax4_4)
ax4_4.set_title('Overall Average Appointment Duration per Specialty')
ax4_4.set_xlabel('Specialty')
ax4_4.set_ylabel('Average Appointment Duration (minutes)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

#place all figures in this list
figure_list = [
    [fig1, fig1_1, fig1_2, fig1_3, fig1_4],
    [fig3, fig3_1, fig3_2, fig3_3, fig3_4],
    [fig4, fig4_1, fig4_2, fig4_3, fig4_4]
]

df_list = [
    [q1_1_df, q1_slice_df, q1_dice_df, q1_drilldown_df, q1_rollup_df],
    [q3_1_df, q3_slice_df, q3_dice_df, q3_drilldown_df, q3_rollup_df],
    [q4_1_df, q4_slice_df, q4_dice_df, q4_drilldown_df, q4_rollup_df]

]
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