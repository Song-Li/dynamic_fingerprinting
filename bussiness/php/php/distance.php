<?php

//example of using distance API
//receive features in json format
if(file_get_contents("php://input")){

    include "uniquemachine.php";

    echo json_encode(distance(json_decode(file_get_contents("php://input"))));

}

?>
