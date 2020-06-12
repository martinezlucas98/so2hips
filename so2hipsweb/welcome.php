<html>
<style>
	th{
		text-align:left;
	}
	table,th,td {
		border: 1px solid grey;
		border-collapse: collapse;
	}
	th,td {
		padding: 5px;
	}
	form{
		border: 3px solid #f1f1f1;
		
	}
	/*input[type=text], input[type=password]{
		padding: 12px 20px;
		margin: 8px 0px;
		display: inline-block;
		border: 1px solid #ccc;
		box-sizing: border-box;
	}
	button{
		padding: 14px 20px;
		margin: 8px 0px;
		border: none;
		cursor: pointer;
	}
	button:hover{
		opacity:0.8;
	}
	.okbtn{background-color: #4CAF50;color: white;}
	.errbtn{background-color: #a8323a;color: white;}
	.warnbtn{background-color: #e3c739;color: white;}*/
</style>
<?php
	session_start();
	if(isset($_SESSION['S_USERNAME']) && !empty($_SESSION['S_USERNAME'])):
		$dbconn = pg_connect($_SESSION['CONN']);
		?>	
		<form action="logout.php" method="post">
			<button type="submit" name="logoutBtn" class="warnbtn">Log Out</button>
			<button name="reloadBtn" onclick="window.location.reload();">Reload Data</button>
		</form>
		<select id="dbtable" name="dbtable" onchange="changeView()">
			<option value="dangerapp">Dangerous Apps</option>
			<option value="processlimits">Resources Limits (Processes)</option>
			<option value="general">Genereal Settings</option>
			<option value="md5sum">MD5SUM Hashes</option>
			<option value="alarms">Alarms Registrated</option>
			<option value="prevention">Preventions Taken</option>
		</select>
		<div id="dangerappDiv">
			<br/>
			<br/>
			<b>Add New:</b>
			<br/>
			<br/>
			<form action="update.php" method="post">
				<input type="text" placeholder="App Name" name="appname" required />
				<button type="submit" name="addDangerapp" class="okbtn">Add</button>
			</form>
			<br/>
			<b>Delete Row:</b>
			<br/>
			<br/>
			<form action="update.php" method="post">
				<input type="text" placeholder="App Name" name="delnameD" required />
				<button type="submit" name="delDangerapp" class="errbtn">Delete</button>
			</form>
			<br/>
			<br/>
			<br/>
			<table style="width:100%">
				<tr>
					<th>App Name</th>
				</tr>
				<?php
					$result = pg_query($dbconn, "SELECT * FROM dangerapp ORDER BY name ASC;");
					if (!$result){echo "1";}
					while ($row = pg_fetch_row($result)){
						//echo "<br> <b>App Name:</b> ".$row[0]."<br>";
						echo "<tr><td>".$row[0]."</td></tr>";
					}
				?>
			</table>

		</div>

		<div id="processlimitsDiv" style="display:none">
			<br/>
			<br/>
			<b>Add New:</b>
			<br/>
			<br/>
			<form action="update.php" method="post">
				<input type="text" placeholder="Process Name" name="processname" required />
				<input type="text" placeholder="Cpu Max %" name="cpumax" required />
				<input type="text" placeholder="RAM Max %" name="memmax" required />
				<input type="text" placeholder="Max runtime" name="maxtime" required />
				<button type="submit" name="addProcesslimits" class="okbtn">Add</button>
			</form>
			<br/>
			<b>Delete Row:</b>
			<br/>
			<br/>
			<form action="update.php" method="post">
				<input type="text" placeholder="Process Name" name="delnameP" required />
				<button type="submit" name="delProcesslimits" class="errbtn">Delete</button>
			</form>
			<br/>
			<br/>
			<br/>
			<table style="width:100%">
				<tr>
					<th>Process Name</th>
					<th>Max CPU %</th>
					<th>Max RAM %</th>
					<th>Max Runtime(ms)</th>
				</tr>
			<?php
				$result = pg_query($dbconn, "SELECT * FROM processlimits ORDER BY name ASC;");
				if (!$result){echo "2";}
				while ($row = pg_fetch_row($result)){
					//echo "<br> <b>Process Name:</b> ".$row[0]." <b>Cpu Max %:</b> ".$row[1]." <b>RAM max %:</b> ".$row[2]." <b>Max runtime:</b> ".$row[3]."<br>";
					echo "<tr><td>".$row[0]."</td><td>".$row[1]."</td><td>".$row[2]."</td><td>".$row[3]."</td></tr>";
				}
			?>
			</table>

		</div>

		<div id="generalDiv" style="display:none">
			<br/>
			<br/>
			<b>Update Info:</b>
			<br/>
			<br/>
			<form action="update.php" method="post">
				<input type="text" placeholder="New IPv4" name="ipv4" required />
				<input type="text" placeholder="New Max mail queue" name="maxmailq" required />
				<button type="submit" name="addGeneral">Update</button>
			</form>
			<br/>
			<br/>
			<br/>
			<table style="width:100%">
				<tr>
					<th>My IPv4</th>
					<th>Max Mail Queue</th>
				</tr>
			<?php

				$result = pg_query($dbconn, "SELECT * FROM general;");
				if (!$result){echo "3";}
				while ($row = pg_fetch_row($result)){
					//echo "<br> <b>My IPv4:</b> ".$row[0]." <b>Max mail queue:</b> ".$row[1]."<br>";
					echo "<tr><td>".$row[0]."</td><td>".$row[1]."</td></tr>";
				}
			?>
			</table>

		</div>

		<div id="md5sumDiv" style="display:none">
			<br/>
			<br/>
			<b>Add New:</b>
			<br/>
			<br/>
			<form action="update.php" method="post">
				<input type="text" placeholder="File Absolute Path" name="filedir" required />
				<input type="text" placeholder="MD5SUM Generated Hash*" name="hash" />
				<button type="submit" name="addMd5sum" class="okbtn">Add</button>
				<br/>
				<a style="font-size: 11px;">*If Hash is left empty then the HIPS will generated on the next run.</a>
			</form>
			<br/>
			<b>Delete Row:</b>
			<br/>
			<br/>
			<form action="update.php" method="post">
				<input type="text" placeholder="File Absolute Path" name="delnameM" required />
				<button type="submit" name="delMd5sum" class="errbtn">Delete</button>
			</form>
			<br/>
			<br/>
			<br/>
			<table style="width:100%">
				<tr>
					<th>File Absolute Path</th>
					<th>MD5SUM Generated Hash</th>
				</tr>
			<?php
				$result = pg_query($dbconn, "SELECT * FROM md5sum ORDER BY dir ASC;");
				if (!$result){echo "4";}
				while ($row = pg_fetch_row($result)){
					//echo "<br> <b>File Absolute Path:</b> ".$row[0]." <b>Hash:</b> ".$row[1]."<br>";
					echo "<tr><td>".$row[0]."</td><td>".$row[1]."</td></tr>";
				}
			?>
			</table>

		</div>

		<div id="alarmsDiv" style="display:none">
			<br/>
			<br/>
			<table style="width:100%">
				<tr>
					<th>Timestamp</th>
					<th>Alarm Message</th>
				</tr>
			<?php
				$result = pg_query($dbconn, "SELECT * FROM alarms ORDER BY time DESC;");
				if (!$result){echo "5";};
				while ($row = pg_fetch_row($result)){
					//echo "<br> <b>Timestamp:</b> ".$row['0']." <b>Alarm:</b>".$row['1'];
					echo "<tr><td>".$row[0]."</td><td>".$row[1]."</td></tr>";
				}
			?>
			</table>
		</div>

		<div id="preventionDiv" style="display:none">
			<br/>
			<br/>
			<table style="width:100%">
				<tr>
					<th>Timestamp</th>
					<th>Action Taken</th>
				</tr>
			<?php
				$result = pg_query($dbconn, "SELECT * FROM prevention ORDER BY time DESC;");
				if (!$result){echo "6";}
				while ($row = pg_fetch_row($result)){
					//echo "<br> <b>Timestamp:</b> ".$row['0']." <b>Action:</b>".$row['1'];
					echo "<tr><td>".$row[0]."</td><td>".$row[1]."</td></tr>";
				}
			?>
			</table>
		</div>

		

<?php else: 
	echo "no session";
	header("Location: index.php");
?>

<?php endif;?>
</html>
<script>
	function changeView(){
		var dbtable = document.getElementById("dbtable");
		//window.alert(dbtable.options[dbtable.selectedIndex].value);
		var selectedDiv = dbtable.options[dbtable.selectedIndex].value + "Div";
		//window.alert(selectedDiv);
		for(var i=0; i<dbtable.length; i++){
			var divId = dbtable.options[i].value + "Div";
			document.getElementById(divId).style.display = "none";
		}
		document.getElementById(selectedDiv).style.display = "block";
		sessionStorage.setItem("currentSelection",dbtable.options[dbtable.selectedIndex].value);
		//window.alert(sessionStorage.getItem("currentSelection"));
	};
	
</script>

<script>
	//document.getElementById("dbtable").onchange = changeView();
	var selStor = sessionStorage.getItem("currentSelection");
	if (selStor != null){
		document.getElementById("dbtable").value = selStor;
		//window.alert(selStor);
		changeView();
	}
</script>

<?php
pg_close($dbconn);
?>
