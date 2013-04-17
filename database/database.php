<?php

date_default_timezone_set('Asia/Calcutta');

$dbUser = 'xxxx';
$dbPass = 'xxxxxx';
$dbHost = 'xxxxxx.mongolab.com';
$dbPort = 'xxxxx';
$dbName = 'xxxxxxxxx';

$allTimeCollectionName           = 'all';
$recentCollectionName            = 'recent';
$errorDistributionCollectionName = 'error';
$logCollectionName               = 'log';
$maxDocuments                    = 100;

function connectToDatabase($dbUser, $dbPass, $dbHost, $dbPort, $dbName) {
    try {
reconnect:
        $database = new MongoClient("mongodb://{$dbUser}:{$dbPass}@{$dbHost}:{$dbPort}/{$dbName}");
    }
    catch (MongoConnectionException $e) {
        goto reconnect;
    }
    return $database->$dbName;
}

$database = connectToDatabase($dbUser, $dbPass, $dbHost, $dbPort, $dbName);

$allTimeCollection           = $database->$allTimeCollectionName;
$recentCollection            = $database->$recentCollectionName;
$errorDistributionCollection = $database->$errorDistributionCollectionName;
$logCollection               = $database->$logCollectionName;

function modifyRecentCollection($name, $sex, $country, $city, $state, $id, $error, $time) {
    global $database, $maxDocuments, $recentCollection;
    if ($database->$recentCollection->count() < $maxDocuments) {
        $database->$recentCollection->insert(array(
            'facebook_id' => $id,
            'error' => $error,
            'time' => $time,
            'name' => $name,
            'sex' => $sex,
            'address' => (object) array(
                'country' => $country,
                'state' => $state,
                'city' => $city
            ),
            'date' => new MongoDate()
        ));
    } else {
        $document = $database->$recentCollection->find()->sort(array(
            "date" => 1
        ))->limit(1)->getNext();
        $database->$recentCollection->update(array(
            "_id" => $document["_id"]
        ), array(
            '$set' => array(
                'facebook_id' => $id,
                'error' => $error,
                'time' => $time,
                'name' => $name,
                'sex' => $sex,
                'address' => (object) array(
                    'country' => $country,
                    'state' => $state,
                    'city' => $city
                ),
                'date' => new MongoDate()
            )
        ));
    }
    return;
}

function modifyAllTimeCollection($name, $sex, $country, $city, $state, $id, $error, $time) {
    global $database, $maxDocuments, $allTimeCollection;
    $cursor = $database->$allTimeCollection->find(array(
        "_id" => $id
    ));
    if ($cursor->count()) {
        $document = $cursor->getNext();
        if ($document['error'] > $error || ($document['error'] == $error && $document['time'] > $time)) {
            $database->$allTimeCollection->update(array(
                "_id" => $document["_id"]
            ), array(
                '$set' => array(
                    'error' => $error,
                    'time' => $time,
                    'name' => $name,
                    'sex' => $sex,
                    'address' => (object) array(
                        'country' => $country,
                        'state' => $state,
                        'city' => $city
                    ),
                    'date' => new MongoDate()
                )
            ));
        }
    } else {
        if ($database->$allTimeCollection->count() < $maxDocuments) {
            $database->$allTimeCollection->insert(array(
                '_id' => $id,
                'error' => $error,
                'time' => $time,
                'name' => $name,
                'sex' => $sex,
                'address' => (object) array(
                    'country' => $country,
                    'state' => $state,
                    'city' => $city
                ),
                'date' => new MongoDate()
            ));
        } else {
            $doc = $database->$allTimeCollection->find(array(), array(
                "_id" => false,
                "error" => true,
                "time" => true
            ))->sort(array(
                "error" => -1,
                "time" => -1
            ))->limit(1)->getNext();
            if ($doc["error"] > $error || ($doc["error"] == $error && $doc["time"] >= $time)) {
                $document = $database->$allTimeCollection->find(array(
                    "error" => $doc["error"],
                    "time" => $doc["time"]
                ), array(
                    "_id" => true
                ))->sort(array(
                    "date" => 1
                ))->limit(1)->getNext();
                $database->$allTimeCollection->remove(array(
                    "_id" => $document['_id']
                ));
                $database->$allTimeCollection->insert(array(
                    "_id" => $id,
                    "error" => $error,
                    "time" => $time,
                    'name' => $name,
                    'sex' => $sex,
                    'address' => (object) array(
                        'country' => $country,
                        'state' => $state,
                        'city' => $city
                    ),
                    "date" => new MongoDate()
                ));
            }
        }
    }
    return;
}

function modifyErrorDistribution($error) {
    global $database, $errorDistributionCollection;
    $error  = round($error, 1, PHP_ROUND_HALF_DOWN);
    $cursor = $database->$errorDistributionCollection->find(array(
        "error" => $error
    ));
    if (!$cursor->hasNext())
        $database->$errorDistributionCollection->insert(array(
            "error" => $error,
            "count" => 1
        ));
    else
        $database->$errorDistributionCollection->update(array(
            "error" => $error
        ), array(
            '$inc' => array(
                "count" => 1
            )
        ));
    return;
}

function updateDatabase($name, $sex, $country, $city, $state, $id, $error, $time) {
    
    $error = (float) $error;
    $time  = (float) $time;
    modifyRecentCollection($name, $sex, $country, $city, $state, $id, $error, $time);
    modifyAllTimeCollection($name, $sex, $country, $city, $state, $id, $error, $time);
    modifyErrorDistribution($error);
    return;
}


function getTop10() {
    global $database, $allTimeCollection;
    $ret    = array();
    $idx    = 0;
    $cursor = $database->$allTimeCollection->find()->sort(array(
        "error" => 1,
        "time" => 1
    ))->limit(10);
    foreach ($cursor as $document) {
        $document['date'] = date('jS F, Y \a\t g:i:s A [\G\M\T P]', $document['date']->sec);
        $ret[$idx]        = $document;
        $idx += 1;
    }
    return json_encode($ret);
}

function getTop100() {
    global $database, $allTimeCollection;
    $ret    = array();
    $idx    = 0;
    $cursor = $database->$allTimeCollection->find()->sort(array(
        "error" => 1,
        "time" => 1
    ));
    foreach ($cursor as $document) {
        $document['date'] = date('jS F, Y \a\t g:i:s A [\G\M\T P]', $document['date']->sec);
        $ret[$idx]        = $document;
        $idx += 1;
    }
    return json_encode(array(
        'type' => 'all',
        'data' => $ret
    ));
}

function getRecent100() {
    global $database, $recentCollection;
    $ret    = array();
    $idx    = 0;
    $cursor = $database->$recentCollection->find()->sort(array(
        "date" => -1
    ));
    foreach ($cursor as $document) {
        $document['date'] = date('jS F, Y \a\t g:i:s A [\G\M\T P]', $document['date']->sec);
        $ret[$idx]        = $document;
        $idx += 1;
    }
    return json_encode(array(
        'type' => 'recent',
        'data' => $ret
    ));
}

function getErrorDistribution() {
    global $database, $errorDistributionCollection;
    $ret    = array();
    $idx    = 0;
    $cursor = $database->$errorDistributionCollection->find()->sort(array("error" => 1));
    foreach ($cursor as $document) {
        $ret[$idx] = $document;
        $idx += 1;
    }
    return json_encode($ret);
}

function logGameInit($name, $sex, $country, $city, $state, $id) {
    global $database, $logCollection;
    $cursor = $database->$logCollection->find(array('_id' => $id));
    if ($cursor->count()) {
        $document = $cursor->getNext();
        $document['count'] += 1;
        array_push($document['logs'], array('sdate' => new MongoDate()));
        $database->$logCollection->save($document);
    } else
        $database->$logCollection->insert(array(
            '_id' => $id,
            'name' => $name,
            'sex' => $sex,
            'address' => (object) array(
                'country' => $country,
                'state' => $state,
                'city' => $city
            ),
            'count' => 1,
	    'best-score-error' => 9999,
	    'best-score-time' => 0,
	    'best-score-date' => new MongoDate(),
            "logs" => (object) array(
                array(
                    'sdate' => new MongoDate()
                )
            )
        ));
    
    return;
}

function logGameCompletion($id, $error, $time) {
    $error = (float) $error;
    $time  = (float) $time;
    global $database, $logCollection;
    $document = $database->$logCollection->find(array('_id' => $id))->getNext();
    $idx = $document['count'] - 1;
    $document['logs'][$idx] = array_merge($document['logs'][$idx], array(
        'error' => $error,
        'time' => $time,
        'fdate' => new MongoDate()
    ));
    if ($error < $document['best-score-error']) {
	$document['best-score-error'] = $error;
	$document['best-score-time'] = $time;
	$document['best-score-date'] = $document['logs'][$idx]['fdate'];
    } elseif ($error == $document['best-score-error'] && $time < $document['best-score-time']) {
	$document['best-score-time'] = $time;
	$document['best-score-date'] = $document['logs'][$idx]['fdate'];
    }
    $database->$logCollection->save($document);

    $document['best-score-date'] = date('jS F, Y \a\t g:i:s A (\G\M\T P)', $document['best-score-date']->sec);
    return json_encode($document);
}

function getBestScore($id) {
    global $database, $logCollection;
    $ret    = array('error' => -1, 'time' => -1, 'date' => -1);
    $message = '';
    $cursor = $database->$logCollection->find(array('_id' => $id));
    if ($cursor->count()) {
        $document = $cursor->getNext();
        if ($document['best-score-error'] != 9999) {
	    $ret['error'] = $document['best-score-error'];
	    $ret['time'] = $document['best-score-time'];
	    $ret['date'] = date('jS F, Y \a\t g:i:s A (\G\M\T P)', $document['best-score-date']->sec);
	}
    }

    if ($ret['error'] == -1 && $ret['time'] == -1 && $ret['date'] == -1)
	$message = "I'm yet to register my score";
    else
	$message = "My best score is <b>" . $ret['error'] . "</b>, in <b>" . $ret['time'] . "</b> sec. Scored on <i>" . $ret['date'] . "</i>";

    return $message;
}

?>
