<?php

if(isset($_POST["hash_value"])){

    include "uniquemachine.php";

    check_exist_picture($_POST["hash_value"]);
}
?>