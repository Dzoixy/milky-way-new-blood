<?php require_once("../includes/auth_check.php"); ?>

<form method="POST" action="save_patient.php">
    <input type="text" name="name" placeholder="Patient Name" required>
    <input type="text" name="national_id" placeholder="National ID" required>
    <input type="number" name="age" placeholder="Age" required>
    <input type="number" step="0.1" name="bmi" placeholder="BMI" required>
    <button type="submit">Save</button>
</form>