
<html>
<head>
<title>jc://music-box/upload/</title>
</head>
<body>
<h1>jc://music-box/upload/</h1>
<?php

$upload_dir  = "../mbox_img/cover_upload";
$myinfofile  = "$upload_dir/_upload_info.txt";
$mytestfile  = "$upload_dir/_upload_test.txt";
$current_dir = getcwd();
$test        = true;


// check and show, if file and metadata is given
if (isset($_FILES['datei']['name'])) {
	$filename   = $_FILES['datei']['name'];
	echo "Filename: $filename<br/>";
	echo "Testfile: $mytestfile<br/>";
	echo "Upload Dir: $upload_dir<br/>";
	echo "Current Dir: $current_dir<br/>";
	}
else {
	echo "Filname: &lt;No filename set&gt;<br/>";
	echo "Testfile: $mytestfile<br/>";
	echo "Upload dir: $upload_dir<br/>";
	echo "Current Dir: $current_dir<br/>";
	}

// test if writing file works ... ?
if ($test) {
	$myfile = fopen($mytestfile, "w");
	fwrite($myfile, "TEST");
	fclose($myfile);
	echo "TEST WRITING ... to: $mytestfile<br/>";
	$myfile    = fopen($mytestfile, "r");
	if ($myfile) {
		while(!feof($myfile)) { $mycontent = fgets($myfile); }
		echo "TEST READING ... $mycontent";
  		}
  	else {
		echo "TEST READING ... ERROR (dir $upload_dir have to be writeable -> try chmod 666)";
		}
	fclose($myfile);
	}
	
// open testfile to write upload information
try {
	$myfile     = fopen($myinfofile, "w"); 
	if ( !$myfile ) { throw new Exception('File open failed.'); }
	fwrite($myfile, "test\n");
	}
catch ( Exception $e ) {
  	echo "ERROR: $e";
	} 

// upload and process file
if (isset($_FILES['upload_dir'])) {
	$upload_dir = $_FILES['upload_dir'];
	$upload_dir = str_replace("_","/",$upload_dir);
	fwrite($myfile, "changed upload dir to: $upload_dir\n");
	}

if (isset($_FILES['album_name'])) {
	$end = "";
	$filename = "";
	fwrite($myfile, "set album_name to: ".$_FILES['album_name']."\n");
	}

if (isset($_FILES['datei'])) {

	foreach ($_FILES["datei"]["error"] as $key => $error) {
		fwrite($myfile, " --" . $key . "/" . $error . "--\n");
		}

	fwrite($myfile, "Filename: ".$upload_dir."/".basename($_FILES['datei']['name'])."\n");
	$upload = move_uploaded_file($_FILES['datei']['tmp_name'], $upload_dir ."/". basename($_FILES['datei']['name']));

	if ($upload) { fwrite($myfile, " - Upload erfolgt: " . basename($_FILES['datei']['name'])); }
	else         { fwrite($myfile, " - Fehler bei Upload: " . basename($_FILES['datei']['name'])); }

     //move_uploaded_file($_FILES['datei']['tmp_name'], basename($_FILES['datei']['name']));
     //move_uploaded_file($_FILES['datei']['tmp_name'], '/var/www/html/app/cover_upload/'.basename($_FILES['datei']['name']));

}
else {
	fwrite(myfile, "Keine Datei ...");
	}
	
fclose($myfile);

?>
</body>
</html>
