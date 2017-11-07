<?php

function connect(){
    $file_handle = fopen("ignore", "r");
    $host = fgets($file_handle);
    $host = str_replace(array("\r", "\n"), '', $host);
    $username = fgets($file_handle);
    $username = str_replace(array("\r", "\n"), '', $username);
    $password = fgets($file_handle);
    $password = str_replace(array("\r", "\n"), '', $password);
    fclose($file_handle);

    $conn = new mysqli($host, $username, $password);

    if($conn->connect_error)die("Connection failed: " . $conn->connect_error);

    echo "Connected successfully!";

    return $conn;
}

function run_sql($conn, $sql){
    $result = $conn->query($sql);
    return $result->fetch_all();
}
?>
