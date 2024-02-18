import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

from data import sales_data, inventory_data, product_data, sales_year_data, inventory_month_data

#Create charts
# Chart 1: Bar chart of sales data

fig1, ax1 = plt.subplots()
ax1.bar(sales_data.keys(), sales_data.values())
ax1.set_title("Sales by Product")
ax1.set_xlabel("Product")
ax1.set_ylabel("Sales")

# Chart 2: Horizontal bar chart of inventory data
fig2, ax2 = plt.subplots()
ax2.barh(list(inventory_data.keys()), inventory_data.values())
ax2.set_title("Inventory by Product")
ax2.set_xlabel("Inventory")
ax2.set_ylabel("Product")

# Chart 3: Pie chart of product data
fig3, ax3 = plt.subplots()
ax3.pie(product_data.values(), labels=product_data.keys(), autopct='%1.1f%%')
ax3.set_title("Product \nBreakdown")

# Chart 4: Line chart of sales by year
fig4, ax4 = plt.subplots()
ax4.plot(list(sales_year_data.keys()), list(sales_year_data.values()))
ax4.set_title("Sales by Year")
ax4.set_xlabel("Year")
ax4.set_ylabel("Sales")

# Chart 5: Area chart of inventory by month
fig5, ax5 = plt.subplots()
ax5.fill_between(inventory_month_data.keys(),
                 inventory_month_data.values())
ax5.set_title("Inventory by Month")
ax5.set_xlabel("Month")
ax5.set_ylabel("Inventory")

#place all figures in this list
figure_list = [
    [fig1, fig4], 
    [fig2, fig5], 
    [fig3,]

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

    

button_update(0, 0, False)
root.mainloop()