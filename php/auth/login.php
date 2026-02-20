<?php session_start(); ?>
<!DOCTYPE html>
<html>
<head>
    <title>Login - Milky Way</title>
    <link rel="stylesheet" href="../static/style.css">
</head>
<body>

<div class="login-container">
    <h2>Milky Way Clinical DSS</h2>

    <form method="POST" action="login_process.php">
        <input type="text" name="username" placeholder="Username" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">LOGIN</button>
    </form>

    <?php
    if(isset($_SESSION['error'])){
        echo "<p style='color:red'>" . $_SESSION['error'] . "</p>";
        unset($_SESSION['error']);
    }
    ?>
</div>

</body>
</html>