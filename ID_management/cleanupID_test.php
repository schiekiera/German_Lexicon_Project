<?php 
$filename = "IDs_test.txt";
$file = file($filename);
$check = $_POST['ID'];
foreach($file as $key => $row) {
    if(preg_match("/^($check)$/", $row)) {
        unset($file[$key]);
    }
}
file_put_contents($filename, $file);
?>