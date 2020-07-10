# SO2HIPS
(HIPS desarrollado en Python3 para SO2. Año 2020)

So2hips es un sistema de prevención de instrusos (para el host) elaborado completamente en python.

¿Qué hace So2hips?  
1. Monitorea la cola de mail alertando al usuario por mail y tomando acciones si el tamaño de la cola supera un valor establecido por el usuario.
2. Monitorea los registros /var/log/maillog, /var/log/messages y /var/log/secure en busca de patrones de ataques SMTP bloqueando al atacante en caso de detectarlo (lo agrega a una lista negra) y alertando al usuario por mail.
3. Monitorea los dispositivos de red conectados y alerta al usuario por mail en caso de encontrar un disopsitivo enmodo promiscuo.
4. Busca procesos/aplicaciones sniffers (u otras especificadas por el usuario) ejecutandose. En caso de encontrarlos, alerta al usuario por mail, pone la applicacion en un directorio de cuarentena y mata al proceso.
5. Monitorea el uso de los recursos (CPU, RAM, tiempo de ejcución) por parte de los procesos. En caso de detectar que un proceso esta utilizando más de lo especificado, se alerta al usuario por mail.
6. Verifica las IP conectadas al servidor.
7. Verifica si alguna maquina (o usuario) se encuentra realizando fuzzling. Luego de 5 intentos fallidos de acceder a un directorio web, se le alerta al usuario por mail y se procede a bloquear la IP de dicha maquina. Obviando la IP del servidor.
8. Verifica si algunos archivos especificados en la base de datos fue alterado. Lo hace mediante la comparacion de hashes MD5SUM. En caso de ser así, alerta al usuario por mail para que este tome las medidas deseadas.
9. Crea automaticamente los hashes MD5SUm de los archivos especificados enla base de datos.
10. Busca archivos shells en el directorio /tmp. En el caso de encontrar alguno, alerta al usuario por mail y pone el archivo en cuarentena.
11. Busca archivos scripts (.py .c .cpp .ruby .sh .exe .php .pl) en el directorio /tmp. En el caso de encontrar alguno, alerta al usuario por mail y pone el archivo en cuarentena.
12. Verifica los registros /var/log/messages y /var/log/secure en busca de Authentication Failures. Alerta al usuario por mail si es aue los encuentra.
13. Todas las alarmas realizadas y acciones de prevencion quedan registradas en los archivos /var/log/hips/alarmas_log y /var/log/hips/prevencion_log respectivamente. También son almacenados en la base de datos para poder verlos desde la pagina web incluida.
14. Cuenta con una simple interfaz web para el monitoreo de las alertas y acciones de prevención así como para configurar el sistema So2hips a gusto (Esto también puede hacerlo directamente desde PostgreSQL.



### Requerimientos
Para que So2hips funcione correctamente es necesario que el usuario cuente con algunas librerias especificas y una base de datos PostgreSQL.  
A continuación veremos como isntalar estas librerias y configurar el sistema.

Aclaracion: el proceso de instalación está explicado para CENTOS/RHE (utilizando yum install). Si cuenta con otra distribución de Linux, utilice el comando adecuando (ejemplo: apt-get install)

##### Python3
Como So2hips fue desarrollado completamente en Python3 requiere que el ordenador/servidor cuente con Python3 instalado.

Para instalarlo ejecutamos el comando: `sudo yum install python3`

También necesitaremos las herramientas de desarrollador de python 3: `sudo yum install python3python3-devel`


##### GCC
Como es lógico, el ordenador/servidor debe contar con GCC para la correcta ejecución de los scripts
`sudo yum install gcc`


##### PIP3
El ordenador/servidor debe contar con pip3 para poder instalar librerias de python.  
Instalamos pip3: `sudo yum install python3-pip`

En caso de que no cuente con el repositorio necesario (suele ocurrir en CentOS) ejecute:  
`sudo yum install epel-release`


##### Psutil
La libreria de python de psutil es necesaria para que So2hips pueda ejecutar los comandos en linux correctamente.  
Ejecutamos: `pip3 isntall psutil`


##### PostgreSQL
So2hips se conecta directamente a una base PostgreSQL, por lo que es necesaria contar con una de antemano.  
Lo conseguimos ejecutando los dos siguientes comandos:  
`sudo yum isntall postgresql-client`  
`sudo yum install postgres1l-devel`

Levantamos el servicio de postgres: `sudo systemctl start postgresql`

(**Si necesita más ayuda para instalar postgres en CentOS haga click [aqui](https://www.hostinger.com/tutorials/how-to-install-postgresql-on-centos-7/)** )


### Configuración de PostgreSQL
Para que So2hips funcione adecuadamente, necesitamos crear la base de datos y tablas correspondientes, asi como también un usuario con los permisos necesarios.

A continuación se encuentra un chart con el nombre de las tablas necesarias y una descripción breve de ella:

| Nombre de la tabla 	| Descripción                                                                                                       	|
|--------------------	|-------------------------------------------------------------------------------------------------------------------	|
| dangerapp          	| Contiene el nombre de aplicaciones maliciosas como sniffers las cuales no queremos en nuestro ordenador/servidor. 	|
| processlimits      	| Contiene el uso máximo de CPU, memoria RAM, y máximo tiempo de vida de los procesos queridos.                     	|
| general            	| Contiene información general: IP de nuestro ordenador/servidor y el numero máximo de mails permitidos en cola.    	|
| md5sum             	| Contiene archivos junto con sus hashes MD5SUM.                                                                    	|
| alarms             	| Contiene todas las alarmas generadas por So2hips junto con su timestamp.                                           	|
| prevention         	| Contiene todas las medidas de prevención tomadas ante las alarmas junto con su timestamp.                          	|


Para poder crear una base de datos y luego las tablas, debemos utilizar el usuario predeterminado de postgres: _postgres_  
Ejecutamos:  
`sudo su - postgres`  
Nos conectamos a la base de datos ejecutando: `psql`  
Ahora podemos ejecutar queries como de costumbre.


##### Creación de la base de datos
La base de datos que utiliza So2hips se debe llamar hipsdb  
La creamos ejecutando: `CREATE DATABASE hipsdb;`

### Creación de las tablas necesarias
Ejecutando los siguientes comandos crearemos todas las tablas mencionadas anteriormente:  
`CREATE TABLE dangerapp (names varchar(25));`  
`CREATE TABLE processlimits (name varchar(25),cpu real, mem real, maxtime bigint);`  
`CREATE TABLE general (myipv4 varchar(15),maxmailq int);`  
`CREATE TABLE md5sum (dir varchar, hash varchar);`  
`CREATE TABLE alarms (time TIMESTAMP, alarm varchar);`  
`CREATE TABLE prevention (time TIMESTAMP, action varchar);`  

### Población de las tablas
Para evitar inconvenientes es necesario poblar la tabla _general_ con la IP del ordenador/servidor.  
Lo hacemos mediante el siguiente comando:  
`INSERT INTO general (myipv4) VALUES ('your_ip_here');`  
Donde _your_ip_here_ es la IP de su ordenador/servidor. Por ejemplo: '192.168.0.11' (**debe de estar entre comillas simple**)

Algunos de los sniffers mas comunes o utilizados son:  
solarwinds, prtg, manageengine, omnipeek, tcpdump, windump, wireshark, fiddler, netresec, capsa.  
Por lo que recomendamos cargarlos a la tabla de _dangerapp_. Si quiere hacerlo, lo puede realizar ejecutando:

`INSERT INTO dangerapp (name) VALUES ('solarwinds'),('prtg'),('manageengine'),('omnipeek'),('tcpdump'),('windump'),('wireshark'),('fiddler'),('netresec'),('capsa'),('ethereal');`

\*Usted puede editar las tablas cuando desee por lo que no es necesario agregarlo ahora mismo\*


### Creación de un usuario
Ahora debemos crear un usuario para acceder a la base de datos. Este usuario junto con su contraseña también seran las credenciales para iniciar sesión en la página web para adminsitrar las tablas.

Para crear un usuario ejecutamos: `CREATE USER your_username_here WITH PASSWORD 'your_password_here';`  
Donde _your_username_here_ es el nombre de usuario que usted quiere y _your_password_here_ la contraseña que quiere para este usuario.  
(**la contraseña _your_password_here_ debe de ir entre comillas simples**)

Ahora le damos los permisos de escritura, lectura, actualizar, etc sobre esta base de datos (hipsdb) al usuario que recién creamos:  
`GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO your_username_here;`  

Ya terminamos de configurar los usuarios y las tablas por lo que ya podemos salir de PostgreSQL, ejecutamos:  
`\q`  
Y luego para salir del usuario _postrges_:  
`exit`

### Configuración del archivo pg_hba.conf
PostgreSQL por default utiliza el metodo de autentiación _ident_, lo que significa que uno solo puede conectarse a PostgreSQL utilizando el nombre de usuario de su maquina.  
Ejemplo: si tu nombre de usuario en la computadora es sysadmin, entonces solo podras conectarte a la base de datos con ese nombre de usuario.  
Esto complica las cosas a la hora de acceder a la base de datos desde una pagina web. Por lo tando lo cambiaremos al modo de autenticación _md5_ (autenticación por contraseña)  

Para hacerlo debemos editar el archivo pg_hba.conf el cual se encuentra en /var/lib/pgsql/data/
Enconces cambiamos al directorio correspondiente: `sudo cd /var/lib/pgsql/data/`

Lo abrimos con algun editor de texto, nosotros lo haremos con nano:  
`sudo nano pg_hba.conf`

Hacia el final, cambiamos donde dice `local        all       all              ident`  o `local        all       all              peer`  
por  
`local        all       all             md5` 

Tambien cambiamos donde dice `host        all       all      127.0.0.1/32       ident`  o `host        all       all      127.0.0.1/32       peer`  
por  
`host        all       all      127.0.0.1/32       md5`

Por último agregamos al final `host        all       all      your_ip_here       md5`  
Donde _your_ip_here_ es la IP de su ordenador/servidor junto con su mascara. Por ejemplo: 192.168.0.11/24
Guardamos el archivo. En nano sería presionando las teclas Ctrl+x

Reiniciamos el servidor postgres para que se actualicen los cambios realizados en el archivo pg_hba.conf: `sudo service postgresql restart` o `sudo systemctl restart postgresql`



### Configuración del sistema
So2hips necesita de algunos archivos y directorios que usted debe crearlos.


##### POSTFIX Blacklist
Necesitamos crear o habilitar el archivo de lista d=negra de POSTFIX para almacenar los mails banneados/bloqueados.

Cambiamos de directorio: `sudo cd /etc/postfix`  
Creamos el archivo de la lista negra: `sudo touch check_sender_access`  
Ejecutamos: `sudo postman hash:sender_access`  
Abrimos el archivo main.cf con algun editor de texto, por ejemplo nano: `sudo nano main.cf`  
Agregamos la siguiente linea dentro del archivo: `smtpd_recipient_restrictions = check_sender_access hash:/etc/postfix/sender_access`  
Guardamos y cerramos el archivo, en nano lo hacemos con: Ctrl+x  
Reiniciamos el servicio de postfix para que se actualicen los cambios: `service postfix restart`



##### Creación del directorio y archivos para los log
'sudo mkdir /var/log/hips'  
'sudo touch /var/log/hips/alarmas_log'  
'sudo touch /var/log/hips/prevencion_log'  
En alarmas_log se guardará el registro de alarmas producidas por So2hips y en prevencion_log un registro de las acciones tomadas contra tales alarmas.



### Instalar la interfaz/página web al servidor
Siplemente debemos mover el contenido dentro de la carpeta so2hipsweb al directorio de su servidor web.  
Si usted esta utilizando apache (comunmente incluido en CentOS) este directorio es: /var/www/html/
Para poner el servidor apache online ejecutamos: `sudo systemctl service start httpd`

Si no cuenta con el servidor web puede instalarlo ejecutando: `sudo yum install httpd`


## So2hips ya se encuentra listo para usar!!!
#### Recuerde que las credenciales de la interfaz web son las mismas que el usuario de postgres que usted ha creado en los pasos anteriores.
