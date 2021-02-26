from Qubic_Marker import *

Pod_ID = 555556655
check_in_time = "2021-01-26 10:00:00"
check_out_time = "2021-01-26 11:00:00"
current_time = datetime.now().time()
Current_Pod = Qubic(Pod_ID, check_in_time, check_out_time)

if __name__ == '__main__':
    # # Check in process by using marker
    # Current_Pod.Check_In(current_time)
    #
    # # Check out process by using marker
    # Current_Pod.Check_Out(current_time)

    # User detection by using computer vision only
    Current_Pod.User_Detection()