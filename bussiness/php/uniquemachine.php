<?php

function check_exist_picture($hash_value){

    include "fingerprints.php";

    $sql_str = "SELECT count(dataurl) FROM pictures WHERE dataurl='" . $hash_value . "'";

    $conn = connect();
    $res = run_sql($conn, $sql_str, true);

    $get = 0;

    if ($res[0][0] > 0){
        $get = 1;
    }
    $conn->close();

    return $get;
}

function update_features($json){

    include "fingerprints.php";

    $feature_list = array(
        "agent",
        "accept",
        "encoding",
        "language",
        "langsDetected",
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
        "adBlock",
        "cpucores",
        "canvastest",
        "audio",
        "ccaudio",
        "hybridaudio",
        "touchSupport",
        "doNotTrack"
    );

    $result = json_decode($json);

    $unique_label = $result->uniquelabel;
    $features = array();

    foreach ($result as $feature => $value){
        if (!in_array($feature, $feature_list) && $feature != "clientid")
            continue;

        #fix the bug for N/A for cpu_cores
        if ($feature == 'cpu_cores'){
            $value = (int)$value;
        }

        $features[$feature] = $value;
    }

    doUpdateFeatures($unique_label, $features);
    return json_encode(array("finished" => "[" . implode(",",array_keys($features)) . "]" ));
}

function initialize($hashCookie){

    include "fingerprints.php";

    $IP = getRealIpAddr();

    $id_str = $IP . time();

    $unique_label = sha1($id_str);

    $headers = apache_request_headers();
    $cookie = $hashCookie;

    $sql_str = "SELECT count(id) FROM cookies WHERE cookie = '" . $cookie . "'";

    $conn = connect();
    $res = run_sql($conn,$sql_str,true);

    if ($res[0][0] == 0) {
        $cookie = $unique_label;
        $sql_str = "INSERT INTO cookies (cookie) VALUES ('" . $cookie . "')";
        run_sql($conn, $sql_str);
    }
    $conn->close();

    doInit($unique_label, $cookie);

    return $unique_label . ',' . $cookie;
}

function store_picture($image_b64){
    include "fingerprints.php";

    // get ID for this picture

    $hash_value = sha1($image_b64);

    $conn = connect();
    $sql_str = "INSERT INTO pictures (dataurl) VALUES ('" . $hash_value . "')";
    run_sql($conn, $sql_str);

    // open the output file for writing
    $ifp = fopen( "pictures/" . $hash_value . ".png", "wb" );

    // split the string on commas
    $data = explode( ',', $image_b64 );

    // we could add validation here with ensuring count( $data ) > 1
    fwrite( $ifp, base64_decode( $data[ 1 ] ) );

    // clean up the file resource
    fclose( $ifp );

    return $hash_value;
}

function install($hashCookie, $pictureHash, $image_b64, $features){
    include "fingerprints.php";

    initialize($hashCookie);

    if(check_exist_picture($pictureHash) > 0)
        store_picture($image_b64);

    update_features($features);
}

function distance($hashCookie){
    include "fingerprints.php";

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
        "cpucores",
        "canvastest",
        "audio",
        "ccaudio",
        "hybridaudio"
    );

    $conn = connect();

    $sql_str = "DESCRIBE features";
    $res = run_sql($conn, $sql_str,true);
    $attrs = array();

    foreach ($res as $attr){
        array_push($attrs, $attr[0]);
    }

    $ID = $hashCookie;

    $sql_str = "SELECT * FROM features";
    $all_records = run_sql($conn,$sql_str,true);

    $sql_str = "SELECT * FROM features WHERE label='" . $ID . "'";

    $aim_record = run_sql($conn,$sql_str,true)[0];
    $num_attr = count($aim_record);
    $cur_max = -1 ;
    $max_record = "";
    $cur_same = 0;

    foreach ($all_records as $record){
        $cur_same = 0;
        if ($ID == $record[22]){
            continue;
        }

        foreach ($feature_list as $feature){
            $i = array_search($feature, $attrs);

            if($record[$i] == $aim_record[$i]){


                $cur_same += 1;
            }

            else{
            }
        }

        if ($cur_same > $cur_max){
            $cur_max = $cur_same;
            $max_record = $record[21];
        }
    }

    return $cur_max / count($feature_list) . ", " . $max_record;
}

?>