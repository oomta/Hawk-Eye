<?php

$name = $_POST['name'];
$gender = $_POST['gender'];
$id = $_POST['id'];
$city = $_POST['city'];
$state = $_POST['state'];
$country = $_POST['country'];

require('./database.php');

logGameInit($name, $gender, $country, $city, $state, $id);

?>
