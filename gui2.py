import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

#Create charts
######################################################################################################################################
# Chart 1: Get yearly count of appointments, grouped into virtual and non-virtual appointments, for each city (roll-up & drill down) #
######################################################################################################################################
df = pd.read_csv("datasets/number1/1.csv")
#group data by city
grouped = df.groupby('city')
fig1, ax1 = plt.subplots()
#plot data for each city
for city, group in grouped:
    ax1.bar(group['appointment_year'], group['virtual_appointments'], label=f'{city} - Virtual')
    ax1.bar(group['appointment_year'], group['non_virtual_appointments'], label=f'{city} - Non-Virtual')
#set labels
ax1.set_xlabel('Year')
ax1.set_ylabel('Number of Appointments')
ax1.set_title('Appointments by City')
ax1.legend()

#########################################################################
# Chart 1.1: refine by showing yearly count for each province (roll-up) #
#########################################################################
df = pd.read_csv("datasets/number1/1.1.csv")
#group data by province
grouped = df.groupby('province')
fig1_1, ax1_1 = plt.subplots()
#plot data for each province
for province, group in grouped:
    ax1_1.plot(group['appointment_year'], group['virtual_appointments'], label=f'{province} - Virtual')
    ax1_1.plot(group['appointment_year'], group['non_virtual_appointments'], label=f'{province} - Non-Virtual')
#set labels
ax1_1.set_xlabel('Year')
ax1_1.set_ylabel('Number of Appointments')
ax1_1.set_title('Appointments Trend by Province')
ax1_1.legend()
ax1_1.grid(True)

#######################################################################
# Chart 1_2: refine by showing yearly count for each region (roll-up) #
#######################################################################
df = pd.read_csv("datasets/number1/1.2.csv")
#filter data
df_ncr = df[df['region_name'] == "National Capital Region (NCR)"]
fig1_2, ax1_2 = plt.subplots()
#plot data
ax1_2.plot(df_ncr['appointment_year'], df_ncr['virtual_appointments'], label='NCR - Virtual')
ax1_2.plot(df_ncr['appointment_year'], df_ncr['non_virtual_appointments'], label='NCR - Non-Virtual')
#set labels
ax1_2.set_xlabel('Year')
ax1_2.set_ylabel('Number of Appointments')
ax1_2.set_title('NCR Appointments Trend')
ax1_2.legend()
ax1_2.grid(True)

#########################################################################################################
# Chart 1_3: only look at 1 specific year (showing appointments for each city in the year 2020) (slice) #
#########################################################################################################
df = pd.read_csv("datasets/number1/1.3.csv")
#filter data for year 2020
df_2020 = df[df['appointment_year'] == 2020]
fig1_3, ax1_3 = plt.subplots()
#plot data
ax1_3.bar(df_2020['city'], df_2020['virtual_appointments'], label='Virtual Appointments')
ax1_3.bar(df_2020['city'], df_2020['non_virtual_appointments'], bottom=df_2020['virtual_appointments'], label='Non-Virtual Appointments')
#set labels
ax1_3.set_xlabel('City')
ax1_3.set_ylabel('Number of Appointments')
ax1_3.set_title('Appointments in 2020 by City')
ax1_3.legend()
#plt.xticks(rotation=45, ha='right')

################################################################################################
# Chart 1_4: Yearly count of appointments from 2020-2021, for Region IVA (CALABARZON (IV-A)) and Region IVB(MIMAROPA (IV-B)) (dice) #
################################################################################################
df = pd.read_csv("datasets/number1/1.4.csv")
#filter data for region iva and region ivb and years 2020-2021
regions = ["CALABARZON (IV-A)", "MIMAROPA (IV-B)"]
years = [2020, 2021]
df_filtered = df[(df['region_name'].isin(regions)) & (df['appointment_year'].isin(years))]
fig1_4, ax1_4 = plt.subplots()
# group data by region name and year
grouped = df_filtered.groupby(['region_name', 'appointment_year'])
# plot the data
for (region, year), group in grouped:
    ax1_4.plot(group['appointment_year'], group['virtual_appointments'], label=f'{region} - Virtual ({year})', marker='o')
    ax1_4.plot(group['appointment_year'], group['non_virtual_appointments'], label=f'{region} - Non-Virtual ({year})', marker='o')
# set labels
ax1_4.set_xlabel('Year')
ax1_4.set_ylabel('Number of Appointments')
ax1_4.set_title('Yearly Appointments for Regions IVA and IVB')
ax1_4.grid(True)


#######################################################
# Chart 2: Total number of appointments per specialty #
#######################################################
df = pd.read_csv("datasets/number2/2.csv")
fig2, ax2 = plt.subplots()
# plot data as bar chart
ax2.bar(df['specialty'], df['total_appointments'], color='skyblue')
# set labels
ax2.set_xlabel('Specialty')
ax2.set_ylabel('Total Appointments')
ax2.set_title('Total Appointments by Specialty')
# plt.xticks(rotation=45, ha='right')

###########################################################################
# Chart 2.1: refine by showing yearly count of appointments per specialty #
###########################################################################
df = pd.read_csv("datasets/number2/2.1.csv")
fig2_1, ax2_1 = plt.subplots()
# group data by specialty and appointment year
grouped = df.groupby(['specialty', 'appointment_year']).sum().reset_index()
# plot data for each specialty
for specialty, group in grouped.groupby('specialty'):
    ax2_1.plot(group['appointment_year'], group['total_appointments'], label=specialty)
# set labels
ax2_1.set_xlabel('Year')
ax2_1.set_ylabel('Total Appointments')
ax2_1.set_title('Yearly Appointments by Specialty')
ax2_1.legend()
ax2_1.grid(True)

############################################################################
# Chart 2.2: Refine by showing monthly count of appointments per specialty #
############################################################################
df = pd.read_csv("datasets/number2/2.2.csv")
fig2_2, ax2_2 = plt.subplots()
# group data by specialty, appointment year, and appointment month
grouped = df.groupby(['specialty', 'appointment_year', 'appointment_month']).sum().reset_index()
# plot data for each specialty
for specialty, group in grouped.groupby('specialty'):
    ax2_2.plot(group['appointment_month'], group['total_appointments'], label=specialty)
# set labels
ax2_2.set_xlabel('Month')
ax2_2.set_ylabel('Total Appointments')
ax2_2.set_title('Monthly Appointments by Specialty')
ax2_2.legend()
ax2_2.grid(True)

########################################################################################################################################
# Chart 2.3: Refine by filtering appointments in a certain year and specialty (I.E. 2020-2021, ENT / General Medicine, dice operation) #
########################################################################################################################################
df = pd.read_csv("datasets/number2/2.3.csv")
# filter data for the specific specialty and year
specialty = "ENT / General Medicine"
years = [2020, 2021]
df_filtered = df[(df['specialty'] == specialty) & (df['appointment_year'].isin(years))]
fig2_3, ax2_3 = plt.subplots()
# plot data as a bar chart
ax2_3.bar(df_filtered['appointment_year'], df_filtered['total_appointments'], color='skyblue')
# Set labels and title
ax2_3.set_xlabel('Appointment Year')
ax2_3.set_ylabel('Total Appointments')
ax2_3.set_title(f'Total Appointments for {specialty} in {years}')

################################################################################################
# Chart 3: Average number of appointments during a specific day, for each city (monday-sunday) #
################################################################################################
df = pd.read_csv("datasets/number3/3.csv")
fig3, ax3 = plt.subplots()
# plot data as a bar chart
ax3.bar(df['city'], df['avg_appointments_on_monday'], color='skyblue')
# set labels and title
ax3.set_xlabel('City')
ax3.set_ylabel('Average Appointments on Mondays')
ax3.set_title('Average Appointments on Mondays by City')
#plt.xticks(rotation=45, ha='right')

##############################################################################
# Chart 3.1: Refine to group appointment count according to appointment type #
##############################################################################
df = pd.read_csv("datasets/number3/3.1.csv")
fig3_1, ax3_1 = plt.subplots()
# group data by city and appointment type
grouped = df.groupby(['city', 'appttype']).mean().reset_index()
# get unique cities and appointment types
cities = grouped['city'].unique()
appointment_types = grouped['appttype'].unique()
# set width of bars
bar_width = 0.35
# set index for x-axis
index = range(len(cities))
# plot data for each appointment type
for i, appt_type in enumerate(appointment_types):
    avg_appointments = grouped[grouped['appttype'] == appt_type]['avg_appointments_on_monday']
    ax3_1.bar([x + i * bar_width for x in index], avg_appointments, bar_width, label=appt_type)
# set labels and title
ax3_1.set_xlabel('City')
ax3_1.set_ylabel('Average Appointments on Mondays')
ax3_1.set_title('Average Appointments on Mondays by City and Appointment Type')
ax3_1.set_xticks([x + bar_width * (len(appointment_types) - 1) / 2 for x in index])
ax3_1.set_xticklabels(cities)
ax3_1.legend()

########################################################################
# Chart 3.2: Refine to show Appointments in Clinics in a specific city #
########################################################################
df = pd.read_csv("datasets/number3/3.2.csv")
# specify the city you're interested in
city_of_interest = "Manila"
# filter data for the specific city
df_filtered = df[df['city'] == city_of_interest]
# calculate the average number of appointments on Mondays for the city
avg_appointments = df_filtered['avg_appointments_on_monday'].mean()
# create a figure and axis for plotting
fig3_2, ax3_2 = plt.subplots()
# create a bar chart
ax3_2.bar(city_of_interest, avg_appointments, color='skyblue')
# add labels and title
ax3_2.set_xlabel('City')
ax3_2.set_ylabel('Average Appointments on Mondays')
ax3_2.set_title(f'Average Appointments on Mondays in Clinics in {city_of_interest}')
 
##########################################################################################################################################################################
# Chart 4: Average age and average appointment duration of patients taking an appointment, grouped by specialties of doctors (join, patients, appointments, and doctors) #
##########################################################################################################################################################################
df = pd.read_csv("datasets/number4/4.csv")
fig4, ax4 = plt.subplots()
# plot average patient age
ax4.bar(df['mainspecialty'], df['average_patient_age'], color='skyblue', label='Average Patient Age')
# create a second y-axis for appointment duration
ax4i = ax4.twinx()
ax4i.bar(df['mainspecialty'], df['average_appointment_duration_minutes'], color='orange', label='Average Appointment Duration')
# add labels and title
ax4.set_xlabel('Specialty')
ax4.set_ylabel('Average Patient Age')
ax4i.set_ylabel('Average Appointment Duration (minutes)')
ax4.set_title('Average Patient Age and Appointment Duration by Specialty')

#############################################################################################
# Chart 4.1: refine to group appointments according to virtual and non virtual appointments #
#############################################################################################
df = pd.read_csv("datasets/number4/4.1.csv")
fig4_1, ax4_1 = plt.subplots()
# group data by main specialty and virtual status
grouped = df.groupby(['mainspecialty', 'isvirtual'])
# set the bar width
bar_width = 0.35
# plot bars for each group
bar_positions = range(len(grouped))
for i, ((specialty, isvirtual), group) in enumerate(grouped):
    ax4_1.bar(i - bar_width/2, group['average_patient_age'], bar_width, label=f'{specialty} - {"Virtual" if isvirtual == 1 else "Non-Virtual"}', color='skyblue')
    ax4_1.bar(i + bar_width/2, group['average_appointment_duration_minutes'], bar_width, color='orange')
# set labels
ax4_1.set_xlabel('Specialty and Virtual Status')
ax4_1.set_ylabel('Average Patient Age / Appointment Duration (minutes)')
ax4_1.set_title('Average Patient Age and Appointment Duration by Specialty and Virtual Status')
ax4_1.set_xticks(range(len(grouped)))
ax4_1.set_xticklabels([f'{specialty}\n{"Virtual" if isvirtual == 1 else "Non-Virtual"}' for (specialty, isvirtual), _ in grouped])
ax4_1.legend()

#####################################################################################
# Chart 4.1.1: FURTHER refine to group appointments according to gender of patients #
#####################################################################################
df = pd.read_csv("datasets/number4/4.1.1.csv")
# Create a figure and axis for plotting
fig4_1_1, ax4_1_1 = plt.subplots()

# Group data by main specialty, virtual status, and gender
grouped = df.groupby(['mainspecialty', 'isvirtual', 'gender'])

# Set the bar width
bar_width = 0.2

# Define colors for each gender
colors = {'FEMALE': 'skyblue', 'MALE': 'orange'}

# Plot bars for each group
bar_positions = range(len(grouped))
for i, ((specialty, isvirtual, gender), group) in enumerate(grouped):
    ax4_1_1.bar(i, group['average_patient_age'], bar_width, label=f'{specialty} - {"Virtual" if isvirtual == 1 else "Non-Virtual"} - {gender}', color=colors[gender])

# Add labels and title
ax4_1_1.set_xlabel('Specialty, Virtual Status, and Gender')
ax4_1_1.set_ylabel('Average Patient Age')
ax4_1_1.set_title('Average Patient Age by Specialty, Virtual Status, and Gender')
ax4_1_1.set_xticks(range(len(grouped)))
ax4_1_1.set_xticklabels([f'{specialty}\n{"Virtual" if isvirtual == 1 else "Non-Virtual"} - {gender}' for (specialty, isvirtual, gender), _ in grouped], rotation=45, ha='right', fontsize=5)

# Add a legend with custom handles
handles, labels = ax4_1_1.get_legend_handles_labels()
ax4_1_1.legend(handles, labels)

#place all figures in this list
figure_list = [
    [fig1, fig1_1, fig1_2, fig1_3, fig1_4],
    [fig2, fig2_1, fig2_2, fig2_3],
    [fig3, fig3_1, fig3_2], 
    [fig4, fig4_1, fig4_1_1]
]

#GUI
root = tk.Tk()
root.title('OLAP Application')

side_frame = tk.Frame(root, padx=5, pady=5)
side_frame.pack(side="left", padx=5,pady=5, fill="y")

canvas1 = FigureCanvasTkAgg(fig1, root)

def button_update(image_number, refinement_number):
    global canvas1
    global side_frame

    image_number = image_number % len(figure_list)
    
    side_frame.grid_forget()
    for child in side_frame.winfo_children():
        child.destroy()

    canvas1.get_tk_widget().pack_forget()
    canvas1 = FigureCanvasTkAgg(figure_list[image_number][refinement_number], root)
    canvas1.draw()
    canvas1.get_tk_widget().pack(side="right", fill="both", expand=True)
    
    button_back = tk.Button(side_frame, text = "<<", command=lambda: button_update(image_number-1, 0), width=5)
    curr_fig = tk.Label(text="Fig: "+str(image_number+1), master=side_frame, width=5, pady=20)
    curr_ref = tk.Label(text="Ref: "+chr(ord('`')+refinement_number+1), master=side_frame, width=5)
    button_next = tk.Button(side_frame, text = ">>", command=lambda: button_update(image_number+1, 0), width=5)

    button_back.grid(row=0, column=0)
    curr_fig.grid(row=0, column=1)
    curr_ref.grid(row=1, column=1)
    button_next.grid(row=0, column=2)

    for i in range(len(figure_list[image_number])):
        tk.Button(side_frame, text = chr(ord('`')+i+1), command=lambda i=i: button_update(image_number, i), width=8).grid(row=i+2,column=1, pady=2)

    

button_update(0, 0)
root.mainloop()