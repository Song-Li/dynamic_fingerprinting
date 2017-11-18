<?php

if(file_get_contents("php://input")){

    include "uniquemachine.php";

    echo install(json_decode(file_get_contents("php://input")));

}

?>