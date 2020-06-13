<?php
echo "we in\n";
session_start();
$dbconn = pg_connect($_SESSION['CONN']);
$updateQuery = '';
if(isset($_POST['addDangerapp'])){
	$name = $_POST['appname'];
	$updateQuery = "INSERT INTO dangerapp (name) VALUES ('$name');";
	unset($_POST['addDangerapp']);
	echo "danger done";
}elseif(isset($_POST['addProcesslimits'])){
	$processName = $_POST['processname'];
	$maxCpu = $_POST['cpumax'];
	$maxMem = $_POST['memmax'];
	$maxTime = $_POST['maxtime'];
	$updateQuery = "INSERT INTO processlimits (name,cpu,mem,maxtime) VALUES ('$processName','$maxCpu','$maxMem','$maxTime');";
	unset($_POST['addProcesslimits']);
	echo "process done";
}elseif(isset($_POST['addGeneral'])){
	$ipv4 = $_POST['ipv4'];
	$maxmailq = $_POST['maxmailq'];
	$email = $_POST['email'];
	$email_pass = $_POST['email_pass'];
	$max_ssh = $_POST['max_ssh'];
	$max_fuzz = $_POST['max_fuzz'];
	$updateQuery = "DElETE FROM general WHERE myipv4 IS NOT NULL;INSERT INTO general (myipv4,maxmailq,email,email_pass,max_ssh,max_fuzz) VALUES ('$ipv4','$maxmailq','$email','$email_pass','$max_ssh','$max_fuzz');";
	unset($_POST['addGeneral']);
	echo "general done";
}elseif(isset($_POST['addMd5sum'])){
	$dir = $_POST['filedir'];
	$hash = $_POST['hash'];
	$updateQuery = "INSERT INTO md5sum (dir,hash) VALUES ('$dir','$hash');";
	unset($_POST['addMd5sum']);
	echo "md5sum done";
}elseif(isset($_POST['delDangerapp'])){
	$nameD = $_POST['delnameD'];
	$updateQuery = "DELETE FROM dangerapp WHERE name = '$nameD';";
	unset($_POST['delDangerapp']);
	echo "del danger done";
}elseif(isset($_POST['delProcesslimits'])){
	$nameP = $_POST['delnameP'];
	$updateQuery = "DELETE FROM processlimits WHERE name = '$nameP';";
	unset($_POST['delProcesslimits']);
	echo "del process done";
}elseif(isset($_POST['delMd5sum'])){
	$dirM = $_POST['delnameM'];
	$updateQuery = "DELETE FROM md5sum WHERE dir = '$dirM';";
	unset($_POST['addMd5sum']);
	echo "del md5sum done";
}else{
	echo "Oops...Algo salio mal.";
	exit;
}

$result = pg_query($dbconn, $updateQuery);
if (!$result){
	echo "Ocurrio un error. Verifique la conexion a la BD y vuelva a intentarlo.\n";
	exit;
}
pg_close($dbconn);
header("Location: welcome.php");
?>
