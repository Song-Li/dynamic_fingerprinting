<?php

function connect(){
    //echo "connect" . "<br>";
    $file_handle = fopen("ignore", "r");
    $host = fgets($file_handle);
    $host = str_replace(array("\r", "\n"), '', $host);
    $username = fgets($file_handle);
    $username = str_replace(array("\r", "\n"), '', $username);
    $password = fgets($file_handle);
    $password = str_replace(array("\r", "\n"), '', $password);
    $dbname = fgets($file_handle);
    $dbname = str_replace(array("\r", "\n"), '', $dbname);
    fclose($file_handle);
    $conn = new mysqli($host, $username, $password, $dbname);

    if($conn->connect_error)die("Connection failed: " . $conn->connect_error);

    //echo "Connected successfully!";

    return $conn;
}

function run_sql($conn, $sql, $isQuery = false){
    //print "<br>" . $sql . "<br>";
    $result = $conn->query($sql);

    if($isQuery)return $result->fetch_all();
    else return $result;
}
?>
