<?php
session_start();
if(isset($_SESSION['S_USERNAME']) && !empty($_SESSION['S_USERNAME'])&&isset($_POST['logoutBtn'])){
	unset($_SESSION['CONN']);
	unset($_SESSION['S_USERNAME']);
	unset($_POST['logoutBtn']);
	session_destroy();
}
header("Location: index.php");
?>
