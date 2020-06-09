import os
import subprocess
import psutil
import socket
import psycopg2

def connect_to_db():
	preferences_dict = {'dangerapp':'', 'processlimits':[], 'myip':'', 'maxmailq' : '', 'md5sum': []}
	credential_ok=False
	while(credential_ok is not True):
		print("Please enter the following data (press enter for default value)\n")
		#my_host = input("Enter host (default: localhost) :  ")
		#my_port = int(input("Enter port (default: 5432) :  "))
		my_user = input("Enter username (default postgres) :  ")
		my_passwd = input("Enter password (default postgres) :  ")
		my_db = input("Enter database (default postgres) :  ")
		try:
			conn = psycopg2.connect(database="hipsdb", user="root", password="testpwd")
			credential_ok = True
		except:
			print("\n\n\nSomething went wrong. Please check your credentials and try again\n\n\n")
	
	cursor = conn.cursor()
	dangerapp_query = "SELECT * FROM dangerapp"
	processlimits_query = "SELECT * FROM processlimits"
	general_query = "SELECT * FROM general"
	md5sum_query = "SELECT hash FROM md5sum"
	md5sum_create_query = "SELECT dir FROM md5sum WHERE hash IS NULL"
	
	cursor.execute(dangerapp_query)
	data = cursor.fetchall()
	data_str = ''
	for row in data:
		data_str+=row[0]+'|'
	
	if(data_str != ''):	
		preferences_dict['dangerapp']=data_str[:-1]
	#print(preferences_dict['dangerapp'])


	cursor.execute(processlimits_query)
	data = cursor.fetchall()
	data_list = []
	for row in data:
		data_list.append({'name':row[0], 'cpu_max_usage':row[1], 'mem_max_usage':row[3], 'max_run_time':row[3]})
		
	preferences_dict['processlimits']=data_list
	
	
	cursor.execute(general_query)
	data = cursor.fetchall()
	for row in data:
		preferences_dict['myip'] = row[0]
		preferences_dict['maxmailq'] = row[1]

	cursor.execute(md5sum_create_query)
	data = cursor.fetchall()
	was_updated = False
	for row in data:
		update_hash_query = 'UPDATE md5sum SET hash=\''+create_md5sum_hash(row[0])+'\' WHERE dir=\''+row[0]+'\';'
		cursor.execute(update_hash_query)
		was_updated = True
	conn.commit()
	
	if(was_updated is not True):
		cursor.execute(md5sum_query)
		data = cursor.fetchall()
		data_list = []
		for row in data:
			data_list.append(row[0])
			
		preferences_dict['md5sum']=data_list
		
		
	else:
		cursor.close()
		conn.close()
		conn = psycopg2.connect(database="hipsdb", user="root", password="testpwd")
		cursor = conn.cursor()
		
		cursor.execute(md5sum_query)
		data = cursor.fetchall()
		data_list = []
		for row in data:
			data_list.append(row[0])
			
		preferences_dict['md5sum']=data_list

	cursor.close()
	conn.close()
		
	return preferences_dict
		
		

def is_program(name):
        #Ve si el archivo `name` existe
        from shutil import which
        print (which(name)) #is not None
        print ('\n')

#print(is_program("wget"))

def check_files_is_program(list):
        #nothing yet
        print('')

def check_mailq(MAX_Q_COUNT):
	p = subprocess.Popen("mailq", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	print(output.decode("utf-8"))
	#print('\n')
	mail_list = output.decode("utf-8").splitlines()
	if len(mail_list) > MAX_Q_COUNT:
		print("Do something\n")


def check_promisc_devs(P_DIR ):
	p_off = subprocess.Popen("cat "+P_DIR+" | grep \"left promisc\"", stdout=subprocess.PIPE, shell=True)
	(output_off, err) = p_off.communicate()
	data_off = output_off.decode("utf-8")
	list_off = data_off.splitlines()
	l_off = len(list_off)
	
	p_on = subprocess.Popen("cat "+P_DIR+" | grep \"entered promisc\"", stdout=subprocess.PIPE, shell=True)
	(output_on, err) = p_on.communicate()
	data_on = output_on.decode("utf-8")
	list_on = data_on.splitlines()
	l_on = len(list_on)
	
	if l_off != l_on:
		#print("Smth is in promisc mode\n")
		compare = []
		devices_on = []
		for line in list_off:
			compare.append(line.split()[-4])
		for line in list_on:
			compare.append(line.split()[-4])
		
		dict_counter = {i:compare.count(i) for i in compare}
		for device in dict_counter:
			if dict_counter[device]%2 != 0:
				devices_on.append(device)
		for device in devices_on:
			print(''+device+' :: Promiscuous mode ON\n')

def check_promisc_apps(P_APP_LIST):
	p = subprocess.Popen("ps axo pid,command | grep -E '"+P_APP_LIST+"' | grep -v '"+P_APP_LIST+"'", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	print(output.decode("utf-8"))
	print('\n')	

def check_promisc(P_DIR, P_APP_LIST):
	check_promisc_devs(P_DIR)
	check_promisc_apps(P_APP_LIST)
	
	
def process_usage(PROCESS_USAGE_LIMITS):
	process_list = list()
	for proc in psutil.process_iter():
		process_dict = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time'])
		process_list.append(process_dict)
		
	for proc in process_list:
		print(proc)
	print('\n')
	
	
def check_ip_connected():
	IPs_connected = subprocess.Popen("netstat -tu 2>/dev/null", stdout=subprocess.PIPE, shell=True)
	(output, err) = IPs_connected.communicate()
	print(output.decode("utf-8"))
	print('\n')

def check_invalid_dir(MY_IP):
	p = subprocess.Popen("cat /var/log/httpd/access_log | grep -v "+MY_IP+" | grep -v ::1 | grep 404", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	print(output.decode("utf-8"))
	print('\n')
			
def check_md5sum(MD5SUM_LIST):
	md5_tmp_dir = '/tmp/so2hipshashes.md5'
	for my_hash in MD5SUM_LIST:
		subprocess.Popen("echo "+my_hash+" >> "+md5_tmp_dir, stdout=subprocess.PIPE, shell=True)
	p =subprocess.Popen("md5sum -c "+md5_tmp_dir, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	print(output.decode("utf-8"))
	print('\n')
	#subprocess.Popen("rm "+md5_tmp_dir, stdout=subprocess.PIPE, shell=True)

def create_md5sum_hash(dir_str):
	p =subprocess.Popen("md5sum "+dir_str, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	print(output.decode("utf-8"))
	print('\n')
	return output.decode("utf-8")[:-1]
	
def main():
	data_list = connect_to_db()
	
	MY_IP = data_list['myip']
	MAX_Q_COUNT = data_list['maxmailq']
	P_DIR = '/var/log/messages'
	P_APP_LIST = data_list['dangerapp']
	PROCESS_USAGE_LIMITS = data_list['processlimits']
	MD5SUM_LIST= data_list['md5sum']
	
	if os.path.isfile(P_DIR) is not True:
		P_DIR = '/var/log/syslog'
	#print(''+P_DIR+'\n')
	#ciclo main
	#check_mailq(MAX_Q_COUNT)
	#is_program("wget")
	#is_program("asdfgh")
	#check_promisc(P_DIR, P_APP_LIST)
	#process_usage(PROCESS_USAGE_LIMITS)
	#check_ip_connected()
	#check_invalid_dir(MY_IP)
	#check_promisc_apps(P_APP_LIST)
	check_md5sum(MD5SUM_LIST)
	return(0)
        
        

if __name__=='__main__':
        main()
        
