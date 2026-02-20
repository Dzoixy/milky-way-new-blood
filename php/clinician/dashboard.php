<?php
require_once("../includes/auth_check.php");
require_once("../config/database.php");

$result = $conn->query("SELECT * FROM patients ORDER BY created_at DESC");
?>

<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
</head>
<body>

<h2>Welcome Dr. <?php echo $_SESSION['name']; ?></h2>

<a href="new_patient.php">Add New Patient</a>
<a href="../auth/logout.php">Logout</a>

<table border="1">
<tr>
    <th>Name</th>
    <th>National ID</th>
    <th>Risk</th>
    <th>Action</th>
</tr>

<?php while($row = $result->fetch_assoc()): ?>
<tr>
    <td><?php echo $row['name']; ?></td>
    <td><?php echo $row['national_id']; ?></td>
    <td><?php echo $row['risk_level']; ?></td>
    <td><a href="view_patient.php?id=<?php echo $row['id']; ?>">View</a></td>
</tr>
<?php endwhile; ?>

</table>

</body>
</html>