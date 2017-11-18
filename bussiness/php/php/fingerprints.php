<?php

include "sql_util.php";

function get_os_from_agent($agent){
    $start_pos = 0;
    $start_pos = strpos($agent, "(");
    $end_pos = strpos($agent, ")");

    return substr($agent, $start_pos + 1, $end_pos - $start_pos - 1);
}

function get_browser_from_agent($agent){
    $start_pos = false;
    if(($start_pos = strpos($agent, "Firefox")) === false )
        if(($start_pos = strpos($agent, "Edge")) === false )
            if(($start_pos = strpos($agent, "Chrome")) === false )
                $start_pos = strpos($agent, "Safari");

    if($start_pos === false)
        return 'unknown';
    else{
        # here use space as the end char
        $end_pos = strpos(substr($agent, $start_pos), " ");
        if($end_pos === false)
                $end_pos = strlen($agent);
        return substr($agent, $start_pos, $end_pos);
    }
}

function getFingerprint($unique_label){

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

    $feature_str = implode(",", $feature_list);

    $sql_str = "select " .$feature_str . " from features where uniquelabel = '" . $unique_label . "'";

    $conn = connect();
    $res = run_sql($conn, $sql_str,true);

    $fingerprint = sha1("[" . implode(",", $res[0]) . "]");

    $sql_str = "UPDATE features SET browserfingerprint='" . $fingerprint . "' WHERE uniquelabel = '" . $unique_label . "';";
    run_sql($conn, $sql_str);

    $conn->close();

    return $fingerprint;
}

function doUpdateFeatures($unique_label, $data){

    $update_str = "";

    foreach ($data as $header => $value) {
        $update_str = $update_str . $header . "='" . $value . "',";
    }
    $update_str = substr($update_str, 0, -1);

    $conn = connect();

    $sql_str = "UPDATE features SET " . $update_str . " WHERE uniquelabel ='" . $unique_label . "'";
    $res = run_sql($conn, $sql_str);

    $conn->close();

    getFingerprint($unique_label);

    return $res;
}

function getRealIpAddr()
{
    if (!empty($_SERVER['HTTP_CLIENT_IP']))   //check ip from share internet
    {
        $ip=$_SERVER['HTTP_CLIENT_IP'];
    }
    elseif (!empty($_SERVER['HTTP_X_FORWARDED_FOR']))   //to check ip is pass from proxy
    {
        $ip=$_SERVER['HTTP_X_FORWARDED_FOR'];
    }
    else
    {
        $ip=$_SERVER['REMOTE_ADDR'];
    }
    return $ip;
}

function doInit($unique_label, $cookie){

    $result = array();
    $agent = "";
    $accept = "";
    $encoding = "";
    $language = "";
    $IP = "";

    $headers = apache_request_headers();

    try {
        $agent = $headers["User-Agent"];
        $accept = $headers["Accept"];
        $encoding = $headers["Accept-Encoding"];
        $language = $headers["Accept-Language"];
        $IP = getRealIpAddr();
    } catch (Exception $e) {
    }


    # create a new record in features table
    $sql_str = "INSERT INTO features (uniquelabel, IP) VALUES ('" . $unique_label . "','" . $IP . "')";

    $conn = connect();
    run_sql($conn,$sql_str);
    $conn->close();

    # update the statics
    $result['agent'] = $agent;
    $result['accept'] = $accept;
    $result['encoding'] = $encoding;
    $result['language'] = $language;
    $result['label'] = $cookie;
    return doUpdateFeatures($unique_label, $result);
}

?>
