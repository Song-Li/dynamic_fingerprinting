<?php


if(isset($_POST['cookie'])){

    include "uniquemachine.php";

    echo initialize($_POST['cookie']);
}

?>