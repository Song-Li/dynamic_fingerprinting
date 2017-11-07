<?php

include 'fingerprints.php';

$recordID = $_POST["recordID"];
echo getFingerprint($recordID);

?>
