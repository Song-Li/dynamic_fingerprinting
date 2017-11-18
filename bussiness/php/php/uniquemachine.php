<?php

include "fingerprints.php";

function check_exist_picture($hash_value)
{

    $sql_str = "SELECT count(dataurl) FROM pictures WHERE dataurl='" . $hash_value . "'";

    $conn = connect();
    $res = run_sql($conn, $sql_str, true);

    $get = 0;

    if ($res[0][0] > 0) {
        $get = 1;
    }
    $conn->close();

    return $get;
}

function update_features($json, $unique_label)
{

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

    $features = array();

    foreach ($json as $feature => $value) {
        if (!in_array($feature, $feature_list) && $feature != "clientid")
            continue;

        #fix the bug for N/A for cpu_cores
        if ($feature == 'cpu_cores') {
            $value = (int)$value;
        }

        $features[$feature] = $value;
    }

    doUpdateFeatures($unique_label, $features);
    return json_encode(array("finished" => "[" . implode(",", array_keys($features)) . "]"));
}

function initialize($hashCookie)
{

    $IP = getRealIpAddr();

    $id_str = $IP . time();

    $unique_label = sha1($id_str);

    if ($hashCookie != "undefined" && $hashCookie != "") $cookie = $hashCookie;
    else $cookie = "NULL";

    if ($cookie != "NULL") {

        $sql_str = "SELECT count(id) FROM cookies WHERE cookie = '" . $cookie . "'";

        $conn = connect();
        $res = run_sql($conn, $sql_str, true);

        if ($res[0][0] == 0) {
            $cookie = $unique_label;
            $sql_str = "INSERT INTO cookies (cookie) VALUES ('" . $cookie . "')";
            run_sql($conn, $sql_str);
        }
        $conn->close();

    }

    doInit($unique_label, $cookie);

    return $unique_label;
}

function store_picture($hash_value, $image_b64)
{

    $conn = connect();
    $sql_str = "INSERT INTO pictures (dataurl) VALUES ('" . $hash_value . "')";
    run_sql($conn, $sql_str);

    // split the string on commas
    $data = explode(',', urldecode($image_b64));

    file_put_contents("../pictures/" . $hash_value . ".png", base64_decode($data[1]));

    return $hash_value;
}

function install($features)
{

    $unique_label = initialize($features->label);

    if (check_exist_picture($features->canvastest) == 0)
        store_picture($features->canvastest, $features->image_b64);

    update_features($features, $unique_label);

    //return $unique_label;
}

function distance($features)
{

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
    $res = run_sql($conn, $sql_str, true);
    $attrs = array();

    foreach ($res as $attr) {
        array_push($attrs, $attr[0]);
    }
    $target = array_search("label", $attrs);

    $sql_str = "SELECT * FROM features";
    $all_records = run_sql($conn, $sql_str, true);

    $num_attr = count($feature_list);
    $cur_max = 0;
    $max_record = "NULL";
    $cur_same = 0;

    foreach ($all_records as $record) {
        if ($record[$target] == "NULL") continue;
        $cur_same = 0;

        foreach ($features as $feature => $value) {
            $i = array_search($feature, $attrs);

            if ($record[$i] == $value) {
                $cur_same += 1;
            }

        }

        if ($cur_same > $cur_max) {
            $cur_max = $cur_same;
            $max_record = $record[$target];
        }
    }

    return $cur_max / count($feature_list) . ", " . $max_record;
}

?>