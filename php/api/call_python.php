<?php
function callPython($data) {

    $url = "https://milky-way-hi44.onrender.com";

    $ch = curl_init($url);

    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_HTTPHEADER, [
        'Content-Type: application/json'
    ]);
    curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));

    $response = curl_exec($ch);

    if(curl_errno($ch)){
        die("Error: ".curl_error($ch));
    }

    curl_close($ch);

    return json_decode($response, true);
}
?>