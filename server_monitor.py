import tempfile
import os, sys
from datetime import datetime
import subprocess
import re
import time
import shlex

class server_monitor():
    def __init__(self):
#         self.now = datetime.now()
#         self.temp_dir = self.make_temp_direcoty()
        
        return
    
    def make_temp_direcoty(self, now): # make temperatary directory for saving temp file
        
        os.makedirs('/home/ec2-user/server_monitor/logs', exist_ok= True)
        temp_dir = tempfile.mkdtemp(prefix=now.strftime("%Y_%b_%d_%Hh_%Mm_"), dir = '/home/ec2-user/server_monitor/logs/')
        
        return temp_dir
    
    def make_blender_temp_file(self, temp_dir): # make temperatary file for saving logs
        
        temp_file = tempfile.NamedTemporaryFile(prefix='blender_log_', dir = temp_dir, delete=False)
        print("blender aux logs will be stored in {}".format(temp_file.name))
        
        return temp_file
    
    def make_io_stat_temp_file(self, temp_dir): # make temperatary file for saving logs
        
        temp_file = tempfile.NamedTemporaryFile(prefix='io_stat_', dir = temp_dir, delete=False)
        print("io_stat aux logs will be stored in {}".format(temp_file.name))
        
        return temp_file
    

    def ps_aux(self): # ps aux in shell
        command = "ps aux"  # the shell command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
        aux_return = process.communicate()

        return aux_return[0]
    
    def io_stat(self): # io_stat in shell
        
        command = "iostat -m 60 -t -y -h -z 1"  # the shell command
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=None, shell=True)
        aux_return = process.communicate()

        return aux_return[0]
    
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
            blender_list.extend('\n')
            b_ret = bytes("\n".join(blender_list), 'utf-8')
            name = tmp.name
            tmp.write(b_ret)
            tmp.read() # Read the contents using tmp.read()
            print("Blender is not running now")
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
        io_high_low = 0
        # datetime object containing current date and time
        io_stat_return = self.io_stat()
#         print(io_stat_return)
        list_= str(io_stat_return, 'UTF-8').splitlines()[2:]
        
        csv_list = []
        
        for index in list_:
            csv_line= ", ".join(re.split(" +", index))
            csv_list.append(csv_line)

        csv_list.append("\n")

        # Checking Device list
        Device_list = list_[4:]
        Device_n_index = Device_list.index('')
        if Device_n_index >= 3 :
            for i, item in enumerate(Device_list):
                try:
                    s_n = item.index('nvme0n1') 
                    nvme_iostat = Device_list[i] + Device_list[i + 1]
                    nvme_tops = re.split(" +", nvme_iostat)[1]
                    if float(nvme_tops) < 3.0:
                        b_ret = bytes("\n".join(csv_list), 'utf-8')
                        tmp.write(b_ret)
                        tmp.read()
                        print('Low Activity')
                        io_high_low = 1
                        return io_high_low
                except:
                    pass

        b_ret = bytes("\n".join(csv_list), 'utf-8')
        tmp.write(b_ret)
        tmp.read()

        return io_high_low
    
    
server_test = server_monitor()
now = datetime.now()
temp_d = server_test.make_temp_direcoty(now)
blender_tmp = server_test.make_blender_temp_file(temp_d)
io_stat_tmp = server_test.make_io_stat_temp_file(temp_d)


while 1:
    io_high_low = server_test.io_stat_output(io_stat_tmp)
    blender_run_or_not = server_test.blender_server_log(blender_tmp)
    print("blender_on/off: {}, io_high_low: {} ".format(blender_run_or_not, io_high_low))
    
    if (blender_run_or_not == 1 ) & (io_high_low == 1):
        print("It's time to turn off computer")
        cmd = shlex.split('sudo shutdown -h 10')
        subprocess.call(cmd)
        
        break
