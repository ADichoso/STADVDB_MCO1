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
# Chart 1: #
############
fig1, ax1 = plt.subplots(figsize=(10, 6))

############
# Chart 1_1: # #Yearly Virtual and Non-virtual Appointments by Province
############
filtered_df = query1_df[(query1_df['virtual_appointments'] > 0) | (query1_df['non_virtual_appointments'] > 0)]
query1_1_df = filtered_df.groupby(['province', 'appointment_year']).agg({
    'virtual_appointments': 'sum',
    'non_virtual_appointments': 'sum'
}).reset_index()
bar_width = 0.35
positions = range(len(query1_1_df['province']))
fig1_1, ax1_1 = plt.subplots(figsize=(10, 6))
ax1_1.bar([pos - bar_width/2 for pos in positions], query1_1_df['virtual_appointments'], bar_width, label='Virtual Appointments')
ax1_1.bar([pos + bar_width/2 for pos in positions], query1_1_df['non_virtual_appointments'], bar_width, label='Non-virtual Appointments')
ax1_1.set_xticks(positions)
ax1_1.set_xticklabels(query1_1_df['province'])
ax1_1.set_xlabel('Province')
ax1_1.set_ylabel('Number of Appointments')
ax1_1.set_title('Yearly Virtual and Non-virtual Appointments by Province')
ax1_1.legend()
plt.xticks(rotation=90, ha='right')
plt.tight_layout()

##############
# Chart 1_3: # only look at 1 specific year (showing appointments for each city in the year 2020) (slice) 
##############
query1_3_df = query1_df.groupby('city').size().reset_index(name='appointment_count')
fig1_3, ax1_3 = plt.subplots(figsize=(10, 6))
ax1_3.bar(query1_3_df['city'], query1_3_df['appointment_count'])
ax1_3.set_title('Appointments per City in 2020')
ax1_3.set_xlabel('City')
ax1_3.set_ylabel('Number of Appointments')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

##############
# Chart 1_4: # Yearly count of appointments from 2020-2021, for National Capital Region (NCR) and CALABARZON (IV-A) (dice) #
##############
query1_4_df = query1_df[((query1_df['region_name'] == 'National Capital Region (NCR)') | (query1_df['region_name'] == 'CALABARZON (IV-A)')) & (query1_df['appointment_year'].isin([2020, 2021]))]
grouped_df = query1_4_df.groupby(['appointment_year', 'region_name']).size().unstack()
fig1_4, ax1_4 = plt.subplots(figsize=(10, 6))
grouped_df .plot(kind='bar', ax=ax1_4)
ax1_4.set_title('Yearly Count of Appointments in NCR and CALABARZON (2020-2021)')
ax1_4.set_xlabel('Year')
ax1_4.set_ylabel('Number of Appointments')
plt.xticks(rotation=0)
ax1_4.legend(title='Region', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()

############
# Chart 3: #
############
query3_1_df = query3_df.groupby(['province', 'day_of_appointment'])['AVG(D.appts)'].mean().unstack()
fig3_1, ax3_1 = plt.subplots(figsize=(10, 6))
query3_1_df.plot(kind='bar', ax=ax3_1)
ax3_1.set_title('Average Appointments per Day of the Week in Each Province')
ax3_1.set_xlabel('Day of the Week')
ax3_1.set_ylabel('Average Appointments')
ax3_1.legend(title='Province', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.xticks(rotation=45)  
plt.tight_layout()

root = tk.Tk()
root.title('Average Appointments per Day of the Week in Each Province')

############
# Chart 4: #
############

############################################################################################
# Chart 4.1: average appointment duration per age range within each specialty (drill-down) #
############################################################################################
query4_1_df = query4_df.groupby(['mainspecialty', 'agerange'])['average_appointment_duration_minutes'].mean().reset_index()
fig4_1, ax4_1 = plt.subplots(figsize=(12, 8))
for key, grp in query4_1_df.groupby('mainspecialty'):
    ax4_1 = grp.plot(ax=ax4_1, kind='line', x='agerange', y='average_appointment_duration_minutes', label=key)
ax4_1.set_title('Average Appointment Duration per Age Range Within Each Specialty')
ax4_1.set_xlabel('Age Range')
ax4_1.set_ylabel('Average Appointment Duration (minutes)')
ax4_1.legend(title='Specialty', bbox_to_anchor=(1.05, 1), loc='upper left')
ax4_1.grid(True)
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

#####################################################################################
# Chart 4.1.1: FURTHER refine to group appointments according to gender of patients #
#####################################################################################
df4_1_1 = pd.read_csv("datasets/number4/4.1.1.csv")
# create a figure and axis for plotting
fig4_1_1, ax4_1_1 = plt.subplots()
# group data by main specialty, virtual status, and gender
grouped = df4_1_1.groupby(['mainspecialty', 'isvirtual', 'gender'])
# set the bar width
bar_width = 0.2
# define colors for each gender
colors = {'FEMALE': 'skyblue', 'MALE': 'orange'}
# plot bars for each group
bar_positions = range(len(grouped))
for i, ((specialty, isvirtual, gender), group) in enumerate(grouped):
    ax4_1_1.bar(i, group['average_patient_age'], bar_width, label=f'{specialty} - {"Virtual" if isvirtual == 1 else "Non-Virtual"} - {gender}', color=colors[gender])
# add labels and title
ax4_1_1.set_xlabel('Specialty, Virtual Status, and Gender')
ax4_1_1.set_ylabel('Average Patient Age')
ax4_1_1.set_title('Average Patient Age by Specialty, Virtual Status, and Gender')
ax4_1_1.set_xticks(range(len(grouped)))
ax4_1_1.set_xticklabels([f'{specialty}\n{"Virtual" if isvirtual == 1 else "Non-Virtual"} - {gender}' for (specialty, isvirtual, gender), _ in grouped], rotation=45, ha='right', fontsize=5)
# add a legend with custom handles
#handles, labels = ax4_1_1.get_legend_handles_labels()
#ax4_1_1.legend(handles, labels)

#place all figures in this list
figure_list = [
    [fig1, fig1_1, fig1_3, fig1_4],
    [fig3_1],
    [fig4_1, fig4_1_1]
]

df_list = [
    [query1_df, query1_1_df, query1_3_df, query1_4_df],
    #[query3_df, query3_1_df, query3_2_df], 
    [query3_1_df],
    [query4_df, query4_1_df, df4_1_1]
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