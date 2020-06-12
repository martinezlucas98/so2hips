<?php	session_start();
	$username = $_POST['username'];
	$password = $_POST['password'];

	/*$username = stripcslashes($username);
	$password = stripcslashes($password);
	$username = mysql_real_escape_string($username);
	$password = mysql_real_escape_string($password);*/

	$conn_string = "dbname=hipsdb user='$username' password='$password'";
	$dbconn = pg_connect($conn_string);
	
	if (!$dbconn){
		echo "Ocurrio un error ";
		$_SESSION['INCORRECT'] = 1;
		header("Location: index.php");
		exit;
	}else{
		echo "hay conexion";
		$_SESSION['S_USERNAME'] = $username;
		$_SESSION['CONN'] = $conn_string;
		unset($_SESSION['INCORRECT']);
		pg_close($dbconn);
		header("Location: welcome.php");
	}
	
	/*$result = pg_query($dbconn, "SELECT * FROM users WHERE username = '$username' AND password = '$password'");
	if (!$result){
		echo "Ocurrio un error\n";
		exit;
	}

	while ($row = pg_fetch_row($result)){
		if ($row['username'] == $username && $row['password'] == $password){
			
		}
	}*/

?>
