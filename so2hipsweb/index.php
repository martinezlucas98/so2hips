<?php
	session_start();
	if(isset($_SESSION['S_USERNAME']) && !empty($_SESSION['S_USERNAME'])){
		header("Location: welcome.php");
	}
?>

<!DOCTYPE html>
<html>
	<head>

		<style>
			form{
				border: 3px solid #f1f1f1;
				margin: 5% 30%;
			}
			input[type=text], input[type=password]{
				width: 100%;
				padding: 12px 20px;
				margin: 8px 0px;
				display: inline-block;
				border: 1px solid #ccc;
				box-sizing: border-box;
			}
			button{
				background-color: #4CAF50;
				color: white;
				padding: 14px 20px;
				margin: 8px 0px;
				border: none;
				cursor: pointer;
				width: 100%;
			}
			button:hover{
				opacity:0.8;
			}
			.imgcontainer{
				text-align: center;
				margin: 24px 0px 12px 0px;
			}
			.container{
				padding: 16px;
			}
			.img.avatar{
				width: 40%;
				border-radius: 50%;
			}
			.failedlogin{
				color:red;
			}

		</style>


		<title>SO2hips / Login</title>
	</head>
	<body>
		<form action="connect.php" method="post">
			<div class="imgcontainer">
				<img src="" alt="Avatar" class="avatar" />
			</div>
			<div class=container">
				<label><b>Username:</b></label>
				<input type="text" placeholder="Enter Username" name="username" required />
				<br/>
				<label><b>Password:&nbsp</b></label>
				<input type="password" placeholder="**********" name="password" required />
				<br/>
				<button type="submit" name="Login">Login</button>
			</div>
			<div class="failedlogin">
				<?php if(isset($_SESSION['INCORRECT'])){echo "Incorrect username or password.";}?>		
			</div>
			Beta
		</form>
	</body>
<script>
sessionStorage.setItem("currentSelection",'dangerapp');
</script>
</html>

