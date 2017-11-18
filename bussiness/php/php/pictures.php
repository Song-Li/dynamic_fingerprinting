<?php

if(isset($_POST["imageBase64"])){

    include "uniquemachine.php";

    store_picture($_POST["imageBase64"]);

    /*include "fingerprints.php";

    // get ID for this picture

    $image_b64 = $_POST["imageBase64"];
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

    echo $hash_value;*/
}
?>