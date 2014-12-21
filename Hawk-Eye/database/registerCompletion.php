<?php

$error = $_POST['error'];
$time = $_POST['time'];
$id = $_POST['id'];

require('./database.php');

echo logGameCompletion($id, $error, $time);

?>
