<?php

//example of using distance API
//receive features in json format
if(file_get_contents("php://input")){

    include "uniquemachine.php";

    echo distance(json_decode(file_get_contents("php://input")));

}

?>
