<?php

$name = $_POST['name'];
$gender = $_POST['gender'];
$id = $_POST['id'];
$city = $_POST['city'];
$state = $_POST['state'];
$country = $_POST['country'];
$error = $_POST['error'];
$time = $_POST['time'];

require('./database.php');

updateDatabase($name, $gender, $country, $city, $state, $id, $error, $time);

?>
