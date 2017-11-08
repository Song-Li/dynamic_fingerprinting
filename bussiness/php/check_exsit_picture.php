<?php

if(isset($_POST["hash_value"])){
    $has_value = $_POST["hash_value"];
    $sql_str = "SELECT count(dataurl) FROM pictures WHERE dataurl='" . $hash_value . "'";

    $conn = connect();
    $res = run_sql($conn, $sql_str, true);
    $conn->close();

    if ($res[0][0] > 0){
        echo '1';
    }
    else{
        echo '0';
    }
}
?>