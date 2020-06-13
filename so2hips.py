import os
import subprocess
import psutil
import socket
import psycopg2
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import time
from datetime import datetime
import random
import string

#Variables globales

#gPASS	(string) almacena la contrasenha del correo que envia las alertas
gPASS = 'holamundo123'

#gMYMAIL	(string) direccion de correo electronico al cual mandar las alertas
gMYMAIL = 'so2hips2020@gmail.com'

#gQUARENTMAIL	(string) informacion: todos los archivos mandados a cuarentena
gQUARENTMAIL = ''

#gQUARENT	(string) absolute path del directorio de cuarentena
gQUARENT = ''


g_my_user = 'root'
g_my_passwd = 'testpwd'
g_my_db = 'hipsdb'



#Funcion: connect_to_db
#
#Establece la conexion con la base de datos postgresql
#
def connect_to_db():
	global g_my_user
	global g_my_passwd
	global g_my_db
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
			conn = psycopg2.connect(database=g_my_db, user=g_my_user, password=g_my_passwd)
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
		data_list.append({'name':row[0], 'cpu_max_usage':row[1], 'mem_max_usage':row[2], 'max_run_time':row[3]})
		
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
		conn = psycopg2.connect(database=g_my_db, user=g_my_user, password=g_my_passwd)
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
        #print (which(name)) #is not None
        #print ('\n')
	if (which(name) is not None):
		print(which(name))
		return (True)
	return (False)

#print(is_program("wget"))

def check_files_is_program(list):
        #nothing yet
        print('')



#Funcion: check_mailq
#
#	Verifica si la cola de mails supero una cantidad maxima determinada
#
#Parametros:
#	MAX_Q_COUNT	(int) numero maximo de mails que pueden estar en cola
#
def check_mailq(MAX_Q_COUNT):
	p = subprocess.Popen("mailq", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	print(output.decode("utf-8"))
	#print('\n')
	mail_list = output.decode("utf-8").splitlines()
	if len(mail_list) > MAX_Q_COUNT:
		print("Do something\n")



#Funcion: check_smtp_maillog
#
#	Verifica si se han enviado una cantidad masiva de mails desde un mismo correo
#	y de ser asi lo pone en una lista negra y alerta. Lo hace revisando el archivo /var/log/maillog
#	Guarda las alertas y las precauciones tomadas en los log correspondientes (Ver: echo_alarmaslog y echo_prevencionlog)
#
def check_smtp_maillog():
	#banned_emails = list()
	counts = dict()
	#email_list = list()
	p = subprocess.Popen("cat  /var/log/maillog | grep -i authid", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	ret_msg = output.decode("utf-8")
	body = ''
	for line in ret_msg.splitlines():
		email = line.split(' ')[7]
		email = email[7:-1] #quitamos el authid= y la coma del final
		if email in counts:
			counts[email]+=1
			if counts[email] == 200: #numero arbitrario
				body = body+email+"\n"
				ban_email(email)
				#banned_emails.append(email)
		else:
			counts[email] = 1
	if body != '' :
		body = "More than 200 emails were sent using: " + body + "\n\n All emails added to blacklist."
		send_email(gMYMAIL,'Alert Type 1 : Masive email',body)
	for key in counts:
		aux = counts[key]
		if aux >= 200:
			echo_alarmaslog(aux+"emails sent using "+key, "SMTP attack",'')
			echo_prevencionlog(key+" was added to postfix email blacklist", "SMTP attack")



#Funcion: check_smtp_messages
#
#	Verifica si se produjeron multiples Authentication Errors hacia un mismo usuario.
#	Lo hace revisando el archivo /var/log/messages
#	Guarda las alertas y las precauciones tomadas en los log correspondientes (Ver: echo_alarmaslog y echo_prevencionlog)
#
def check_smtp_messages():
	counts = dict()
	#email_list = list()
	p = subprocess.Popen("cat  /var/log/messages | grep -i \"[service=smtp]\" | grep -i \"auth failure\"", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	ret_msg = output.decode("utf-8")
	body = ''
	new_passwds = ''
	for line in ret_msg.splitlines():
		user = line.rsplit(' ')[5] #conseguimos [user=condorito]
		user = user[6:-1] #aislamos el username del string anterior
		if user in counts:
			counts[user]+=1
			if counts[user] == 200: #numero arbitrario
				body = body+email+"\n"
				#ban_email(email)
				passwd = get_random_string(random.randint(20,30))
				new_passwds = new_passwds + user + " :: " + passwd
		else:
			counts[user] = 1
	if body != '' :
		body = "More than 200 SMTP auth failure using: " + body + "\n\n All passwords from those users were changed:\n\nUsername :: New_Password\n"+new_passwds
		send_email(gMYMAIL,'Alert Type 1 : Masive SMTP user auth failure',body)
	for key in counts:
		aux = counts[key]
		if aux >= 200:
			echo_alarmaslog(aux+"Authentication failure for "+key, "SMTP attack",'')



#Funcion: check_smtp_secure
#
#	Verifica si se produjeron multiples Authentication Errors hacia un mismo usuario.
#	Lo hace revisando el archivo /var/log/secure
#	Guarda las alertas y las precauciones tomadas en los log correspondientes (Ver: echo_alarmaslog y echo_prevencionlog)
#
def check_smtp_secure():
	counts = dict()
	#email_list = list()
	p = subprocess.Popen("cat  /var/log/secure | grep -i \"(smtp:auth)\" | grep -i \"authentication failure\"", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	ret_msg = output.decode("utf-8")
	body = ''
	new_passwds = ''
	for line in ret_msg.splitlines():
		user = line.rsplit(' ')[1] #conseguimos user=condorito
		user = user[5:] #aislamos el username del string anterior
		if user in counts:
			counts[user]+=1
			if counts[user] == 200: #numero arbitrario
				body = body+email+"\n"
				#ban_email(email)
				passwd = get_random_string(random.randint(20,30))
				new_passwds = new_passwds + user + " :: " + passwd
		else:
			counts[user] = 1
	if body != '' :
		body = "More than 200 SMTP auth failure using: " + body + "\n\n All passwords from those users were changed:\n\nUsername :: New_Password\n"+new_passwds
		send_email(gMYMAIL,'Alert Type 1 : Masive SMTP user auth failure',body)
	for key in counts:
		aux = counts[key]
		if aux >= 200:
			echo_alarmaslog(aux+"Authentication failure for "+key, "SMTP attack",'')




#Funcion: check_smtp_attack
#
#	Invoca a las funciones que buscan patrones de un posible ataque SMTP.
#	(Ver: check_smtp_maillog , check_smtp_messages y check_smtp_secure)
#
def check_smtp_attack():
	check_smtp_maillog()
	check_smtp_messages()
	check_smtp_secure()



#Funcion: check_promisc_devs
#
#	Verifica el estado del modo promiscuos de los dispositivos del ordenador, verificando
#	si fue encendido o apagado ultimamente.
#	En caso de encontrar algun dispositivo en modo promiscuo, lo alerta.
#	Guarda las alertas en el log correspondiente (Ver: echo_alarmaslog)
#
#Parametros:
#	P_DIR	(string)directorio de donde buscar los dispositivos, Normalmente es /var/log/secure
#
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
			global gMYMAIL
			body = ''+device+' :: Promiscuous mode ON\n'
			echo_alarmaslog("The device: "+device+" Promiscuous mode is ON", "Promiscuous mode on device ON",'')
		send_email(gMYMAIL,'Alert Type 2 : Promisc mode ON',body)
			#print(''+device+' :: Promiscuous mode ON\n')



#Funcion: check_promisc_apps
#
#	Busca si se encuentran en el ordenador aplicaciones de sniffers no deseadas.
#	En caso de encontrar alguna, lo alerta, mata el proceso y lo pone en el directorio de cuarentena
#	Guarda las alertas y las precauciones tomadas en los log correspondientes (Ver: echo_alarmaslog y echo_prevencionlog)
#
#Parametros:
#	P_APP_LIST	(string) string con las aplicaciones consideradas peligrosas o no
#			deseadas segun el usuario separadas por medio de "|".
#			Se debe respetar el formato: app1|app2|app3.
#
def check_promisc_apps(P_APP_LIST):
	p = subprocess.Popen("ps axo pid,command | grep -E '"+P_APP_LIST+"' | grep -v '"+P_APP_LIST+"'", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	global gMYMAIL
	body = output.decode("utf-8")
	for line in body.splitlines():
		file_dir = line.split(' ')[1]
		app_pid = line.split(' ')[0]
		kill_process(app_pid)
		send_to_quarentine(file_dir)
		
		echo_alarmaslog("Sniffer app found on "+file_dir, "Sniffer app found",'')
		echo_prevencionlog("Sniffer app found on "+file_dir+" was killed and sent to quarentine folder", "Sniffer app found")
	if len(body)>1:
		body = 'Found sniffers services:\n'+body+"\nAll sniffers were sent to quarentine"
		send_email(gMYMAIL,'Alert Type 2 : Sniffers found',body)
	#print(output.decode("utf-8"))
	#print('\n')	



#Funcion: check_promisc
#
#	Invoca a las funciones encargadas de monitorear los modos promiscuos y sniffers.
#	(Ver: check_promisc_devs y check_promisc_apps)
#
#Parametros:
#	P_DIR	(string)directorio de donde buscar los dispositivos, Normalmente es /var/log/secure
#	P_APP_LIST	(string) string con las aplicaciones consideradas peligrosas o no
#			deseadas segun el usuario separadas por medio de "|".
#			Se debe respetar el formato: app1|app2|app3
def check_promisc(P_DIR, P_APP_LIST):
	check_promisc_devs(P_DIR)
	check_promisc_apps(P_APP_LIST)
	


#Funcion: process_ussage
#
#	Verifica el consumo de recursos de cpu, memoria y tiempo de los procesos activos.
#	En caso de encontrar algun proceso que sobrepase su valor de uso maximo lo alerta y lo mata.
#	(si no lo tiene definido, entonces se utilizaran los valores standard)
#	Guarda las alertas y las precauciones tomadas en los log correspondientes (Ver: echo_alarmaslog y echo_prevencionlog)
#
#Parametros:
#	PROCESS_USAGE_LIMITS	(dict) diccionario con pid , name , cpu_percent , memory_percent , create_time
#				de los procesos.
#				name : (string) nombre del proceso
#				cpu_percent : (float) del 0 al 100, porcenje de uso de la cpu por el profeso
#				memory_percemt : (float) del 0 al 100, porcenje de uso de la RAM por el profeso
#				create_time :	tiempo de creacion del proceso en POSIX
#	
def process_usage(PROCESS_USAGE_LIMITS):
	process_list = list()
	for proc in psutil.process_iter():
		process_dict = proc.as_dict(attrs=['pid', 'name', 'cpu_percent', 'memory_percent', 'create_time'])
		process_list.append(process_dict)
	body = ''
	for proc in process_list:
		max_cpu = 90.000
		max_mem = 90.000
		#max_runtime = 189900.000 #2 dias y 5hs aprox (esta en segundos)
		max_runtime = -1.000
		#print(proc)
		if proc['name'].lower() in (dic['name'].lower() for dic in PROCESS_USAGE_LIMITS):
			max_cpu = dic['cpu_max_usage']
			max_mem = dic['mem_max_usage']
			max_runtime = dic['max_run_time']
		p_runtime = time.time() - proc['create_time']

		exceeded = ''
		cpu_x=mem_x=runtime_x=False
		if proc['cpu_percent'] > max_cpu:
			cpu_x = True
			exceeded=exceeded+'CPU'

		if proc['memory_percent'] > max_mem:
			mem_x = True
			if exceeded != '':
				exceeded=exceeded+' & Memory'
			else:
				exceeded=exceeded+'Memory'

		if (p_runtime > max_runtime and max_runtime >=0.000) :
			runtime_x = True
			if exceeded != '':
				exceeded=exceeded+' & Runtime'
			else:
				exceeded=exceeded+'Runtime'
		if cpu_x or mem_x or runtime_x:
			proc.update({'runtime':str(datetime.timedelta(seconds=int(p_runtime)))})
			proc.update({'reason': 'Exceeded: '+exceeded+' max value for this process'})

			body+=json.dumps(proc)+'\n\n'
			kill_process(proc['pid'])

			echo_alarmaslog("Process exceeded max resources value "+json.dumps(proc), "High resources usage",'')
			echo_prevencionlog("Process killed due to high resources usage "+json.dumps(proc), "High resources usage")
	if body !='':
		body = 'Elevated Process Usage Found:\n\n'+body
		global gMYMAIL
		send_email(gMYMAIL,'Alert Type 2 : Process Usage',body)
		

		
	#print('\n')
	


#Funcion: check_ip_connected
#
#	Obtiene las IP (mediante netstat) de las maquinas conectadas al servidor
#	
def check_ip_connected():
	IPs_connected = subprocess.Popen("netstat -tu 2>/dev/null", stdout=subprocess.PIPE, shell=True)
	(output, err) = IPs_connected.communicate()
	print(output.decode("utf-8"))
	print('\n')



#Funcion: check_invalid_dir
#
#	Verifica si alguna maquina se encuentra realizando fuzzling. Luego de 5 intentos fallidos de
#	acceder a un directorio de la pagina web del servidor, se alerta y bloquea la IP mediante
#	el uso de IPTable
#	Guarda las alertas y las precauciones tomadas en los log correspondientes (Ver: echo_alarmaslog y echo_prevencionlog)
#
#Parametros:
#	MY_IP	(string)IP de la maquina servidor. Para obviarla de la busqueda de intentos fallidos.
#
def check_invalid_dir(MY_IP):
	counts = dict()
	ip_list = list()
	p = subprocess.Popen("cat /var/log/httpd/access_log | grep -v "+MY_IP+" | grep -v ::1 | grep 404", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	#print(output.decode("utf-8"))
	#print('\n')
	ret_msg = output.decode("utf-8")
	print(ret_msg+"\n\n\n\n")
	for line in ret_msg.splitlines():
		#la primera palabra de cada linea es la ip
		first_word = line.split(" ")[0]
		ip_list.append(first_word)
		#print (line+"\n\n\n")
	body = ''
	for ip in ip_list:
		if ip in counts:
			counts[ip]+=1
			if counts[ip] == 5 :
				block_ip(ip)
				body = body + '\n'+ip
			echo_alarmaslog("Ip "+ip+" tried 5 non-existent directories on web server", "Fuzzing atack",ip)
			echo_prevencionlog(ip+" was blocked using IPTables","Fuzzing atack")
		else:
			counts[ip]=1
	if body != '':
		body = "Blocked IP's:"+body
		global gMYMAIL
		send_email(gMYMAIL,'Alert Type 2 : Unknow Web Dir',body)
	#print (counts)
	
		

#Funcion: check_md5sum
#
#	
#	Guarda las alertas y las precauciones tomadas en los log correspondientes (Ver: echo_alarmaslog y echo_prevencionlog)
#
#Parametros:
#	MD5SUM_LIST	(list)lista con el hash producido mediante md5sum. Este se encuentra en el formato: hash dir
#			
def check_md5sum(MD5SUM_LIST):
	body = ''
	md5_tmp_dir = '/tmp/so2hipshashes.md5'
	for my_hash in MD5SUM_LIST:
		subprocess.Popen("echo "+my_hash+" >> "+md5_tmp_dir, stdout=subprocess.PIPE, shell=True)
	p =subprocess.Popen("md5sum -c "+md5_tmp_dir, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	
	if output.decode("utf-8")[-3:-1] != 'OK':
		#print(output.decode("utf-8"))
		body+=output.decode("utf-8")
		file_dir = output.decode("utf-8").split(" ")[0]
		echo_alarmaslog("MD5SUM hash value changed for "+file_dir, "MD5SUM altered","")

	if body != '':
		body = 'MD5SUM hash modified:\n\n' + body	
		global gMYMAIL
		send_email(gMYMAIL,'Alert Type 3 : MD5SUM Modified',body)

	
	#print('\n')
	subprocess.Popen("rm "+md5_tmp_dir, stdout=subprocess.PIPE, shell=True)



#Funcion: create_md5sum_hash
#
#	Crea un hash md5sum utilizando la funcion md5sum para un archivo en especifico
#
#Parametros:
#	dir_str	(string)absolute path del archivo al cual queremos crearle un hash md5sum.
#
#Retorna:
#	(string) el hash producido
#
def create_md5sum_hash(dir_str):
	p =subprocess.Popen("md5sum "+dir_str, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	print(output.decode("utf-8"))
	print('\n')
	return output.decode("utf-8")[:-1]



#Funcion: find_shells
#
#	Inspecciona los archivos dentro de un directorio (de forma recursiva con find) buscando patrones
#	de archivos shell (empiezan con #!).
#	Si los encuentra, alerta y mueve el archivo al directorio de cuarentena.
#	Guarda las alertas y las precauciones tomadas en los log correspondientes (Ver: echo_alarmaslog y echo_prevencionlog)
#
#Parametros:
#	DIR	(string) absolute path del directorio donde se buscaran los shells. Normalmente es /tmp
#	
def find_shells(DIR):
	body = ''
	p =subprocess.Popen("find "+DIR+" -type f", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	#print(output.decode("utf-8"))
	tmp_files_str = output.decode("utf-8")
	for line in tmp_files_str.splitlines():
		cat =subprocess.Popen("cat "+line+" | grep '#!'", stdout=subprocess.PIPE, shell=True)
		(output, err) = cat.communicate()
		txt = output.decode("utf-8")
		if(txt !=''):
			body +='Found posible script in: '+line+'\n'
			send_to_quarentine(line)
			#print('Found posible script in: '+line)
			echo_alarmaslog("Shell found "+line, "Shell found on "+DIR,"")
			echo_prevencionlog("File "+line+" moved to quarentine folder","Shell found on tmp")
	global gMYMAIL
	if body!='':
		body = body +"\nAll files were sent to quarentine."
		send_email(gMYMAIL,'Alert Type 2 : Shells found',body)



#Funcion: find_scripts
#
#	Inspecciona las terminaciones de los archivos dentro de un directorio (de forma recursiva con find)
#	buscando terminaciones clasicas de scripts (ejemplo: .py, .c, .exe, etc).
#	Si los encuentra, alerta y mueve el archivo al directorio de cuarentena.
#	Guarda las alertas y las precauciones tomadas en los log correspondientes (Ver: echo_alarmaslog y echo_prevencionlog)
#
#Parametros:
#	DIR	(string) absolute path del directorio donde se buscaran los scripts. Normalmente es /tmp
#	
def find_scripts(DIR):
	exten = ['py','c','cpp','ruby','sh','exe','php','java','pl']
	cmd = "find "+DIR+" -type f "
	for e in exten:
		cmd+= "-iname '*."+e+"' -o -iname '*."+e+".*' -o "
	if cmd!="find "+DIR+" -type f ":
		cmd = cmd[:-4]
	#print (cmd)
	p =subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	body = ''
	scripts = output.decode("utf-8")
	body = body + scripts
	#print (body)
	#print(output.decode("utf-8"))
	#body = 'Found posible script file/s :\n'+output.decode("utf-8")
	global gMYMAIL
	if body!='':
		for line in scripts.splitlines():
			send_to_quarentine(line)
			echo_alarmaslog("Script found "+line, "Script found on " +DIR,"")
			echo_prevencionlog("File "+line+" moved to quarentine folder","Script found on tmp")
		body = 'Found posible script file/s :\n'+body +"\nAll files were sent to quarentine."
		send_email(gMYMAIL,'Alert Type 2 : Scripts found',body)




#Funcion: check_tmp_dir
#
#	Invoca a las funciones encargadas de monitorear el directorio /tmp en busca de archivos sospechosos.
#	(ver: find_shells y find_scripts)
#	
def check_tmp_dir():
	find_shells("/tmp")
	find_scripts("/tmp")	



#Funcion: check_auths_log
#
#	Busca Authentication Failures en /var/log/secure. En el caso de encontrarlas, los alerta.
#	Guarda las alertas en el log correspondiente (Ver: echo_alarmaslog)
#	
def check_auths_log():
	global gMYMAIL
	p =subprocess.Popen("cat /var/log/secure | grep -i \"authentication failure\"", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	ret_msg = output.decode("utf-8")
	body = ''
	for line in ret_msg.splitlines():
		echo_alarmaslog(line, "Authentication failure","")
		
	body = body + ret_msg
	if body != '':
		send_email(gMYMAIL,'Alert Type 1 : Authentication failure',body)

	

#Funcion: is_script_cron
#
#	Analiza el string que recibe como parametro en busca de terminacionesclasicas de
#	scripts (ejemplo: .py, .c, .exe, etc) y tambien terminaciones combinadas como .php.jpeg
#
#Parametros:
#	line	(string) una linea leida utilizando el comando crontab -l. Se debe respetar el
#		formato: * * * * * [USERNAME_ocional] DIRECTORIO_DE_SCRIPT
#
#Retorna:
#	(string) un string vacio ('') si no se encontro una terminacion de script en el parametro
#	o un string con la informacion de que se detecto un script en la linea pasada como parametro
#
def is_script_cron(line):
	words = line.split()
	path = words[-1]
	exten = ['py','c','cpp','ruby','sh','exe','php','java','pl']
	dirs = path.split("/")
	script = dirs[-1]
	my_extens = script.split(".")
	my_extens.reverse()
	for e in my_extens:
		for e2 in exten:
			if (e==e2):
				if (os.path.isfile(path)):
					info = "Posible script running on cron :: "+line+"\n"
					alarm_type = "Suspicious script running on cron"
					echo_alarmaslog(info, alarm_type,'')
					return (info)
	return ('')



#Funcion: is_shell_cron
#
#	Analiza el string que recibe como parametro, extrae el PATH encontrado en el string
#	y busca dentro de este archivo (si es que existe) el contenido '#!' que marca a los shells	
#
#Parametros:
#	line	(string) una linea leida utilizando el comando crontab -l. Se debe respetar el
#		formato: * * * * * [USERNAME_ocional] DIRECTORIO_DE_SCRIPT
#
#Retorna:
#	(string) un string vacio ('') si el archivo ubicado en el path encontrado en la linea 
#	pasada como parametro no es un shell
#	o un string con la informacion de que se detecto un shell en la linea pasada como parametro
#
def is_shell_cron(line):
	words = line.split()
	path = words[-1]
	cat =subprocess.Popen("cat "+path+" 2> /dev/null | grep '#!'", stdout=subprocess.PIPE, shell=True)
	(output, err) = cat.communicate()
	txt = output.decode("utf-8")
	if(txt !=''):
		info = "Posible shell running on cron:: "+line+"\n"
		alarm_type = "Suspicious shell running on cron"
		echo_alarmaslog(info, alarm_type,'')
		return (info)

	return ('')



#Funcion: is_dangerapp_cron
#
#	Analiza el string que recibe como parametro y verifica si este ejecuta alguna de las
#	aplicaciones consideradas peligrosas o no deseadas segun el usuario.
#	Si los encuentra, alerta al usuario por mail.
#	Guarda las alertas en el log correspondiente (Ver: echo_alarmaslog)
#
#Parametros:
#	line	(string) una linea leida utilizando el comando crontab -l. Se debe respetar el
#		formato: * * * * * [USERNAME_ocional] DIRECTORIO_DE_SCRIPT
#	P_APP_LIST	(string) string con las aplicaciones consideradas peligrosas o no
#			deseadas segun el usuario separadas por medio de "|".
#			Se debe respetar el formato: app1|app2|app3
#
#Retorna:
#	(string) un string vacio ('') si el archivo encontrado en la linea pasada como 
#	parametro no ecorresponde a una de las aplicaciones citadas en P_APP_LIST
#	o un string con la informacion de que se detecto una posible aplicacion no deseada en
#	la linea pasada como parametro
#
def is_dangerapp_cron(line, P_APP_LIST):
	words = line.split()
	path = words[-1]
	dirs = path.split("/")
	app = dirs[-1]
	for e in P_APP_LIST:
		if (e==app):
			info = "Malicious tool running on cron :: "+line+"\n"
			alarm_type = "Suspicious tool running on cron"
			echo_alarmaslog(info, alarm_type,'')
			return (info)
	return ('')
	




#Funcion: check_cron_jobs
#
#	Analiza las lineas retornadas por el comando crontab -l en busca de scripts, shells y
#	aplicaciones o herramientas consideradas peligrosas o no deseadas por el usuario.
#	Lo hace invocando a las funciones is_script_cron , is_shell_cron , is_dangerapp_cron
#	Si los encuentra, alerta al usuario por mail.
#	Guarda las alertas en el log correspondiente (Ver: echo_alarmaslog)
#
#Parametros:
#	P_APP_LIST	(string) string con las aplicaciones consideradas peligrosas o no
#			deseadas segun el usuario separadas por medio de "|".
#			Se debe respetar el formato: app1|app2|app3
#
def check_cron_jobs(P_APP_LIST):
	global gMYMAIL
	app_list = P_APP_LIST.split("|")
	p =subprocess.Popen("crontab -l", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	ret_msg = output.decode("utf-8")
	body_scripts = ''
	body_shells = ''
	body_dangerapp = ''
	for line in ret_msg.splitlines():
		this = is_shell_cron(line)
		if (this != ''):
			body_shells = body_shells + this
		#else:
		this = is_script_cron(line)
		if (this != ''):
			body_scripts = body_scripts + this
		#else
		this = is_dangerapp_cron(line, app_list)
		if (this != ''):
			body_dangerapp = body_dangerapp + this
			
	body = body_scripts + body_shells + body_dangerapp
	if (body != ''):
		body = ""+body+"\nPlease verify and take action."
		send_email(gMYMAIL,'Alert Type 3 : Suspicious files on Cron',body)



#Funcion: send_email
#
#	Establece una conexion con el servidor de email y envia un email desde un correo especifico.
#	Se utiliza para alertar al usuario en caso de encontrar algo sospechoso.
#
#Parametros:
#	email	(string) direccion de correo a la cual se enviara el correo.
#	subject	(string) el subject del correo.
#	body	(string) el contenido del correo. Vendria siendo el mensaje en si.
#
def send_email(email,subject,body):
	global gPASS
	my_address = 'so2hips2020@gmail.com'
	s = smtplib.SMTP('smtp.gmail.com', 587)
	s.starttls()
	s.login(my_address,gPASS)

	msg = MIMEMultipart()
	msg['From']=my_address
	msg['To']=email
	msg['Subject']=subject
	msg.attach(MIMEText(body,'plain'))
	s.send_message(msg)
	del msg
	s.quit()



#Funcion: send_to_quarentine
#
#	Mueve un archivo al directorio de cuarentena.
#
#Parametros:
#	s_file	(string)el archivo (su absolute path) que se movera al directorio de cuarentena.
#
def send_to_quarentine(s_file):
	global gQUARENT
	#print (s_file+'--')
	p =subprocess.Popen("mv "+s_file+" "+gQUARENT, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()



#Funcion: block_ip
#
#	Bloquea una ip dada utilizando IPTables.
#
#Parametros:
#	ip	(string) la IP que se desea boquear o banear.
#
def block_ip(ip):
	p =subprocess.Popen("iptables -A INPUT -s "+ip+" -j DROP", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()

	p =subprocess.Popen("service iptables save", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()




#Funcion: kill_process
#
#	Mata el proceso especificado.
#
#Parametros:
#	pid	(string / int) process id del proceso a matar.
#
def kill_process(pid):
	p =subprocess.Popen("kill -9 "+pid, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()




#Funcion: ban_email
#
#	Agrega una direccion de correo a la lista negra de postfix
#
#Parametros:
#	email	(string) direccion de correo electronico que se desea agregar a la lista negra.
#
def ban_email(email):#verificar si es que no esta
	p =subprocess.Popen("echo \""+email+" REJECT\">>/etc/postfix/sender_access", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()




#Funcion: echo_alarmaslog
#
#	Escribe en el log /var/log/hips/alarmas.log la alarma registrada.
#
#Parametros:
#	alarm		(string) el mlensaje de alarma a registrar.
#	alarm_type	(string) el tipo de la alarma (ej: AMTP attack).
#	ip		(string) IP responsable de generar la alar,a (si es que hay ip, caso contrario ip = '')
#
def echo_alarmaslog(info, alarm_type,ip):
	global g_my_user
	global g_my_passwd
	global g_my_db

	if ip == '':
		ip = "No IP Found"
	date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	msg = ''+date_now+" :: "+alarm_type+" :: "+ip+" :: "+info
	p =subprocess.Popen("echo \""+msg+"\">>/var/log/hips/alarmas.log", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()
	
	try:
		conn = psycopg2.connect(database=g_my_db, user=g_my_user, password=g_my_passwd)
		cursor = conn.cursor()
		query_s = "INSERT INTO alarms (time,alarm) VALUES (TO_TIMESTAMP('"+date_now+"','YYYY-MM-DD HH24:MI:SS'),'"+msg+"');"
		#print (query_s)
		cursor.execute(query_s)
		conn.commit()
		cursor.close()
		conn.close()	
	except:
		print("\n\n\nSomething went wrong. Please check your credentials and try again\n\n\n")
	




#Funcion: echo_prevencionlog
#
#	Escribe en el log /var/log/hips/prevencion.log las medidas de prevencion tomadas debido a una alarma detectada.
#
#Parametros:
#	info	(string) decision tomada (ej: se bloqueo la ip xxx.xxx.xxx.xxx)
#	reason	(string) motivo por el cual se tomo la decision.
#		Similar al parametro alarm_type de echo_alarmaslog.
#
def echo_prevencionlog(info, reason):
	global g_my_user
	global g_my_passwd
	global g_my_db
	
	date_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	msg = ''+date_now+" :: "+info+" :: Reason --> "+reason
	p =subprocess.Popen("echo \""+msg+"\">>/var/log/hips/prevencion.log", stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()

	try:
		conn = psycopg2.connect(database=g_my_db, user=g_my_user, password=g_my_passwd)
		cursor = conn.cursor()
		query_s = "INSERT INTO prevention (time,action) VALUES (TO_TIMESTAMP('"+date_now+"','YYYY-MM-DD HH24:MI:SS'),'"+msg+"');"
		#print (query_s)
		cursor.execute(query_s)
		conn.commit()
		cursor.close()
		conn.close()
	except:
		print("\n\n\nSomething went wrong. Please check your credentials and try again\n\n\n")




#Funcion: main
#
#	Invoca a todas las funciones necesarias para el HIPS repitiendose cada x intervalo de tiempo
#
def main():
	global gQUARENTMAIL
	global gQUARENT
	data_list = connect_to_db()
	gQUARENT = '/quarent'
	MY_IP = data_list['myip']
	MAX_Q_COUNT = data_list['maxmailq']
	P_DIR = '/var/log/messages'
	P_APP_LIST = data_list['dangerapp']
	PROCESS_USAGE_LIMITS = data_list['processlimits']
	MD5SUM_LIST= data_list['md5sum']
	
	if os.path.isfile(P_DIR) is not True:
		P_DIR = '/var/log/syslog'

	if os.path.isdir(gQUARENT) is not True:
		p =subprocess.Popen("mkdir "+gQUARENT, stdout=subprocess.PIPE, shell=True)
		(output, err) = p.communicate()
	
	p =subprocess.Popen("chmod 664 "+gQUARENT, stdout=subprocess.PIPE, shell=True)
	(output, err) = p.communicate()

	#print(''+P_DIR+'\n')
	#ciclo main
	#check_mailq(MAX_Q_COUNT)
	#check_smtp_attack()
	#is_program("wget")
	#is_program("asdfgh")
	#check_promisc(P_DIR, P_APP_LIST)
	#process_usage(PROCESS_USAGE_LIMITS)
	#check_ip_connected()
	#check_invalid_dir(MY_IP) #www.algo.com/noexiste
	#check_promisc_apps(P_APP_LIST)
	#check_md5sum(MD5SUM_LIST)
	#check_tmp_dir()
	#check_auths_log()
	#ban_email("hola@something")
	#ban_email("chau@something")
	#check_cron_jobs(P_APP_LIST)
	#print (P_APP_LIST)
	
	
	if gQUARENTMAIL != '':
		send_email(gMYMAIL,'Files moved to quarentine',gQUARENTMAIL)

	print('DONE')
	return(0)
        
        

if __name__=='__main__':
        main()
        
