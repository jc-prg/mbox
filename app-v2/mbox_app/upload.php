<?php

$myfile     = fopen("./cover_upload/testfile2.txt", "w"); 
$upload_dir = "./cover_upload/";
$filename   = $_FILES['datei']['name'];

if (isset($_FILES['upload_dir'])) {
	$upload_dir = $_FILES['upload_dir'];
        $upload_dir = str_replace("_","/",$upload_dir);
	}

if (isset($_FILES['album_name'])) {
	$end = "";
	$filename = "";
	}

if (isset($_FILES['datei'])) {

	foreach ($_FILES["datei"]["error"] as $key => $error) {
		fwrite($myfile, " --" . $key . "/" . $error . "-- ");
		}

	fwrite($myfile, $upload_dir + basename($_FILES['datei']['name']));
	$upload = move_uploaded_file($_FILES['datei']['tmp_name'], $upload_dir . basename($filename));

	if ($upload) {
		fwrite($myfile, $upload_dir . " - Upload erfolgt: " . basename($_FILES['datei']['name']));
		}
	else {
		fwrite($myfile, $upload_dir . " - Fehler bei Upload: " . basename($_FILES['datei']['name']));
		}

     //move_uploaded_file($_FILES['datei']['tmp_name'], basename($_FILES['datei']['name']));
     //move_uploaded_file($_FILES['datei']['tmp_name'], '/var/www/html/app/cover_upload/'.basename($_FILES['datei']['name']));

//	$myfile = fopen("testfile.txt", "w");
//	fwrite($myfile, "TESTEST: " +basename($_FILES['datei']['name']));
//	fwrite($myfile, $_FILES['datei']['tmp_name'] +"/"+basename($_FILES['datei']['name']));
//	fclose($myfile);
}
else {
	fwrite(myfile, "Keine Datei ...");
	}
fclose($myfile);

?>
