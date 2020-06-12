<?php

	if(True || (isset($_SESSION['S_USERNAME']) && !empty ($_SESSION['S_USERNAME'])):?>
		<!DOCTYPE html>		
			<hmtl>
				<head>
				</head>
				<body>
					<select id=dbtable>
						<option value="dangerapp"></option>
						<option value="processlimits"><option>
						<option value="general"></option>
						<option value="md5sum"></option>
					</select>
				</body>
			</html>
<?php
	else:
		echo "You are not allowed to view this page <a href=\"login.html\">Please login</a>";
	endif;
?>
