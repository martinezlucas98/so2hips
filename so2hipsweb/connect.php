<?php

	$username = $_POST['username'];
	$password = $_POST['password'];

	$username = stripcslashes($username);
	$password = stripcslashes($password);
	$username = mysql_real_escape_string($username);
	$password = mysql_real_escape_string($password);

	$conn_string = "dbname=so2hips user=root password=testpwd";
	$dbconn = pg_connect($conn_string);
	if ($dbconn){
		header("location:welcome.php");
	}
	/*if (!$dbconn){
		echo "Ocurrio un error\n";
		exit;
	}
	
	$result = pg_query($dbconn, "SELECT * FROM users WHERE username = '$username' AND password = '$password'");
	if (!$result){
		echo "Ocurrio un error\n";
		exit;
	}

	while ($row = pg_fetch_row($result)){
		if ($row['username'] == $username && $row['password'] == $password){
			
		}
	}*/

?>
