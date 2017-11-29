<?php

//example of using distance API
//receive features in json format
if(file_get_contents("php://input")){

    include "uniquemachine.php";

    $json = json_decode(file_get_contents("php://input"));

    echo json_encode(distance($json->threshold, file_get_contents("php://input")));

}

?>