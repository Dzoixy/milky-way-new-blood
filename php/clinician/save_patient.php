<?php
require_once("../includes/auth_check.php");
require_once("../config/database.php");

$name = $_POST['name'];
$nid  = $_POST['national_id'];
$age  = $_POST['age'];
$bmi  = $_POST['bmi'];

/* เรียก Python API บน Render */
$api_url = "https://your-render-url.onrender.com/risk/predict";

$data = json_encode([
    "age" => $age,
    "bmi" => $bmi
]);

$options = [
    "http" => [
        "header"  => "Content-Type: application/json\r\n",
        "method"  => "POST",
        "content" => $data,
    ],
];

$context = stream_context_create($options);
$response = file_get_contents($api_url, false, $context);
$result = json_decode($response, true);

$risk_level = $result['risk_level'];

$sql = "INSERT INTO patients (name,national_id,age,bmi,risk_level)
        VALUES ('$name','$nid','$age','$bmi','$risk_level')";

$conn->query($sql);

header("Location: dashboard.php");
exit();