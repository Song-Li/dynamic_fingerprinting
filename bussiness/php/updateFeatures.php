<?php

if($_POST){

    $json = file_get_contents("datas.json");
    $result = json_decode($json);
    $unique_label = $result["uniquelabel"];
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
    echo json_encode(array("finished" => "[" . implode("",array_keys($feature)) . "]" ));

}
?>