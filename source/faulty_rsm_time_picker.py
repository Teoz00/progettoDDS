# from app_graph import ApplicationGraph
# import matplotlib.pyplot as plt
# import time

# case_1 = [5, 2]

# g1 = ApplicationGraph(case_1[0], case_1[1])
# t1 = time.time()
# g1.check_faulty_rsms()
# t1 = time.time() - t1

# print("tempo: ", t1)
# input("PRESS ENTER TO CONTINUE")

# try:
#     with open("./rsm_check_faulty_times.txt", 'a') as file:
#         file.write(f"5, 1 : {t1}")
#         print("Time added to txt")
# except Exception as e:
#     print(f"Error while file writing: {e}")


# g1.stop_event.set()
# g1.cleanup()

# input("PRESS ENTER TO CONTINUE")

import matplotlib.pyplot as plt

def read_data_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                key_part, value_part = line.split(':')
                app_proc, byz_rsm = map(int, key_part.split(','))
                time_value = float(value_part)
                data.append((app_proc, byz_rsm, time_value))
    return data

def plot_bar_chart(data):
    labels = []
    values = []
    
    for app_proc, byz_rsm, time_value in data:
        labels.append(f"AppProc: {app_proc}, Byz RSM: {byz_rsm}")
        values.append(time_value)
    
    plt.bar(labels, values, color='skyblue')

    plt.xlabel('Application Processes e Byzantine RSM')
    plt.ylabel('Time [s]')
    plt.title('Faulty/Byzantine RSM time detection')

    plt.xticks(rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

data = read_data_file("rsm_check_faulty_times.txt")
plot_bar_chart(data)

