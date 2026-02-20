<?php
require_once("../includes/auth_check.php");
require_once("../config/database.php");

$id = $_GET['id'];

$stmt = $conn->prepare("SELECT * FROM patients WHERE id=?");
$stmt->bind_param("i",$id);
$stmt->execute();
$result = $stmt->get_result();
$row = $result->fetch_assoc();
?>

<h2>Patient Detail</h2>
<p>Name: <?php echo $row['name']; ?></p>
<p>National ID: <?php echo $row['national_id']; ?></p>
<p>Age: <?php echo $row['age']; ?></p>
<p>BMI: <?php echo $row['bmi']; ?></p>
<p>Risk Level: <?php echo $row['risk_level']; ?></p>
<p>Risk Score: <?php echo $row['risk_score']; ?></p>