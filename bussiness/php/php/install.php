<?php

//example of using install API
//receive features in json format
if(file_get_contents("php://input")){

    include "uniquemachine.php";

    $json = json_decode(file_get_contents("php://input"));

    echo install($json->label, file_get_contents("php://input"));

}

?>