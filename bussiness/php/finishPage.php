<?php

include 'fingerprints.php';

if(isset($_POST["recordID"])){
    $recordID = $_POST["recordID"];
    echo getFingerprint($recordID);
}

?>
