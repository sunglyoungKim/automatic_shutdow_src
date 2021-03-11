import tempfile
import os, sys
from datetime import datetime
import subprocess
import re
import time
import shlex

class server_monitor():
    def __init__(self):
        self.log_dir = '/home/ec2-user/cloud_render/server_monitor_logs/'
#         self.temp_dir = self.make_temp_direcoty()

       	return
    
    def make_temp_direcoty(self, now): # make temperatary directory for saving temp file
        
        os.makedirs(self.log_dir, exist_ok= True)
        temp_dir = tempfile.mkdtemp(prefix=now.strftime("%Y_%b_%d_%Hh_%Mm_"), dir = self.log_dir)
        
        print("blender server logs will be stored in {}".format(temp_dir))

       	return temp_dir
    
    def make_blender_temp_file(self, temp_dir): # make temperatary file for saving logs

       	temp_file = tempfile.NamedTemporaryFile(prefix='blender_log_', dir = temp_dir, delete=False)
#         print("blender aux logs will be stored in {}".format(temp_file.name))

       	return temp_file
    
    def make_io_stat_temp_file(self, temp_dir): # make temperatary file for saving logs

       	temp_file = tempfile.NamedTemporaryFile(prefix='io_stat_', dir = temp_dir, delete=False)
#         print("io_stat aux logs will be stored in {}".format(temp_file.name))

       	return temp_file
    

    def ps_aux(self): # ps aux in shell
        command = "ps aux"  # the shell command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
        aux_return = process.communicate()

        return aux_return[0]
    
    def io_stat(self): # io_stat in shell

       	command = "sar -n DEV 60  1"  # the shell command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
        io_return = process.communicate()

        return io_return[0]
    
    def blender_server_log(self, tmp): # blender server logs

       	blender_run_or_not = 0

       	aux_return = self.ps_aux()
        aux_return_per_line = str(aux_return, 'UTF-8').splitlines()
        blender_list = []
        current = datetime.now()
#         current.strftime("%b_%d_%Hh_%Mm_%Ss")
        blender_list.append(current.strftime("%b_%d_%Hh_%Mm_%Ss"))
    
        for i, line in enumerate(aux_return_per_line):
            try:
                line.index('blender --background')
                blender_list.append(aux_return_per_line[i]) # find only blender program from ps aux output
            except Exception as e:
                pass
            
            
       	if len(blender_list) == 1:
            blender_list.append('No Blender Activity')
            b_ret = bytes("\n ".join(blender_list)+ '\n ', 'utf-8' )
            name = tmp.name
            tmp.write(b_ret)
            tmp.read() # Read the contents using tmp.read()
#            print("Blender is not running now")
            blender_run_or_not = 1
            return blender_run_or_not


        blender_list.extend('\n')
#         print(blender_list)
        b_ret = bytes("\n".join(blender_list), 'utf-8')
        name = tmp.name
        tmp.write(b_ret)
        tmp.read() # Read the contents using tmp.read()

        return blender_run_or_not
    

    def io_stat_output(self, tmp):
        network_drive_activity = 0

        # datetime object containing current date and time
        io_stat_return = self.io_stat()
#         print(io_stat_return)
        eth0_avg = str(io_stat_return, 'UTF-8').splitlines()[-2]    
        list_= str(io_stat_return, 'UTF-8').splitlines()
        log_time = re.split(" +", list_[2])[0]
        b_ret = bytes(log_time + '\n ' + "\n ".join(list_[-3:]) + "\n ", 'utf-8')
        tmp.write(b_ret)
        tmp.read()

        
        rx_tx_eth0_avg = float(re.split(" +", eth0_avg)[2]) + float(re.split(" +", eth0_avg)[3]) 
        if rx_tx_eth0_avg / 2  < 2.0:
            network_drive_activity = 1
        
        return network_drive_activity
    
if __name__ == "__main__":
    time.sleep(900) #Waiting 15 minutes for Editors
    server_test = server_monitor()
    now = datetime.now()
    temp_d = server_test.make_temp_direcoty(now)
    blender_tmp = server_test.make_blender_temp_file(temp_d)
    io_stat_tmp = server_test.make_io_stat_temp_file(temp_d)

    turn_off = 0 
    while turn_off < 21:
        io_high_low = server_test.io_stat_output(io_stat_tmp)
        blender_run_or_not = server_test.blender_server_log(blender_tmp)
        print("blender_on/off: {}, io_high_low: {} ".format(blender_run_or_not, io_high_low))

        if (blender_run_or_not == 1 ) & (io_high_low == 1):
            turn_off += 1
#             print(turn_off)
        else:
            turn_off = 0

#     print("It's time to turn off computer")
    cmd = shlex.split('sudo shutdown -h 5')
    subprocess.call(cmd)
