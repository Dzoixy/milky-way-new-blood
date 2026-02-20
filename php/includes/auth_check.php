<?php
session_start();
if(!isset($_SESSION['clinician_id'])){
    header("Location: ../auth/login.php");
    exit();
}
?>
