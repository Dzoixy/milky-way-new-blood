<?php
session_start();
require_once("../config/database.php");

$username = $_POST['username'];
$password = $_POST['password'];

$sql = "SELECT * FROM clinicians WHERE username='$username'";
$result = $conn->query($sql);

if($result->num_rows > 0){
    $row = $result->fetch_assoc();
    
    if(password_verify($password, $row['password'])){
        $_SESSION['clinician_id'] = $row['id'];
        $_SESSION['name'] = $row['name'];
        header("Location: ../clinician/dashboard.php");
        exit();
    }
}

$_SESSION['error'] = "Invalid credentials";
header("Location: login.php");
exit();
