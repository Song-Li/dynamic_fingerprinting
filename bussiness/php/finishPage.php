<?php

include 'sql_util.php';

$recordID = $_POST["recordID"];
echo getFingerprint($recordID);

?>
