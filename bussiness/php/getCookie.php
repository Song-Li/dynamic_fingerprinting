<?php

include "fingerprints.php";
include "sql_util.php";

$IP = getRealIpAddr();

$id_str = $IP . time();
$unique_label = sha1(id_str);

$headers = apache_request_headers();
$cookie = $agent = $headers["cookie"];
$sql_str = "SELECT count(id) FROM cookies WHERE cookie = '" . $cookie . "'";

$conn = connect();
$res = run_sql($conn,$sql_str,true);

if ($res[0][0] == 0) {
    $cookie = $unique_label;
    $sql_str = "INSERT INTO cookies (cookie) VALUES ('" + cookie + "')";
    run_sql($conn, $sql_str);
}
$conn->close();

doInit($unique_label, $cookie);
echo $unique_label . ',' . $cookie;
?>