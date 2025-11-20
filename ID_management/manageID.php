<?php 
$filename = "IDs.txt";
$file = file($filename);
$ID = $file[0];
unset($file[0]);
array_push($file,$ID);
file_put_contents($filename, $file);
echo $ID; // Output to update the views live
?>