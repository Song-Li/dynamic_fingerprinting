<?php


if(isset($_POST["recordID"])){

    include "fingerprints.php";

    $recordID = $_POST["recordID"];
    echo getFingerprint($recordID);
}

?>
