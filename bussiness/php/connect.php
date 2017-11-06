<?php

$file_handle = fopen("ignore", "r");
$host = fgets($file_handle);
$username = fgets($file_handle);
$password = fgets($file_handle);
fclose($file_handle);

$conn = new mysqli($host, $username, $password);

if($conn->connect_error)die("Connection failed: " . $conn->connect_error);

echo "Connected successfully!";

?>
