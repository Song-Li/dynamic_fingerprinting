<?php

include 'fingerprints.php';

if(isset($_POST["id"])){

    $feature_list = array(
        "agent",
        "accept",
        "encoding",
        "language",
        "langsdetected",
        "resolution",
        "jsFonts",
        "WebGL",
        "inc",
        "gpu",
        "gpuimgs",
        "timezone",
        "plugins",
        "cookie",
        "localstorage",
        "adblock",
        "cpu_cores",
        "canvas_test",
        "audio",
        "cc_audio",
        "hybrid_audio"
    );

    $conn = connect();

    $sql_str = "DESCRIBE features";
    $res = run_sql($conn, $sql_str,true);
    $attrs = array();

    foreach ($res as $attr){
        array_push($attrs, $attr[0]);
    }

    $ID = $_POST["id"];

    $sql_str = "SELECT * FROM features";
    $all_records = run_sql($conn,$sql_str,true);

    $sql_str = "SELECT * FROM features WHERE id='" . $ID . "'";

    $aim_record = run_sql($conn,$sql_str,true)[0];
    $num_attr = count($aim_record);
    $cur_max = -1 ;
    $max_record = "";
    $cur_same = 0;

    foreach ($all_records as $record){
        $cur_same = 0;
        if ($ID == $record[24]){
            continue;
        }
        foreach ($feature_list as $feature){
            $i = array_search($feature, $attrs);
            if($record[i] == $aim_record[i]){
                $cur_same += 1;
            }
            if ($cur_same > $cur_max){
                $cur_max = $cur_same;
                $max_record = $record[21];
            }
        }
    }

    echo $cur_max / count($feature_list) . ", " . $max_record;

}

?>
