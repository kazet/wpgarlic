<?php

$conn = new mysqli('db1', 'wordpress', 'wordpress', 'wordpress');
$result = $conn->query("SELECT 1 FROM DUAL WHERE '' = " . $_GET['xx']);
if (!$result) {
    die(mysqli_error($conn));
}
