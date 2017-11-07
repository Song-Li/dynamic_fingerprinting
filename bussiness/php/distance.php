<?php

include 'sql_util.php';

$recordID = $_POST["recordID"];
echo getFingerprint($recordID);

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

$sql_str = "DESCRIBE features"
    $res = run_sql($conn, $sql_str);
    $attrs = array();

for attr in res{
    attrs.append(attr[0]);
}

$ID = $_POST["id"];

$sql_str = "SELECT * FROM features";
$all_records = run_sql($sql_str);
$sql_str = "SELECT * FROM features WHERE id=" + ID;
$aim_record = run_sql($sql_str)[0];
num_attr = len(aim_record);
cur_max = -1 ;
max_record = "";
cur_same = 0;
for record in all_records:
    cur_same = 0
    if str(ID) == str(record[24]):
        continue
        for feature in feature_list: 
            i = attrs.index(feature)
            if record[i] == aim_record[i]:
                cur_same += 1
                if cur_same > cur_max:
                    cur_max = cur_same
                    max_record = str(record[21])
                    return str(float(cur_max) / float(len(feature_list))) + ", " + max_record 

?>
