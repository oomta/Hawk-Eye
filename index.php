<?php
    require_once('AppInfo.php');
    if (substr(AppInfo::getUrl(), 0, 8) != 'https://' && $_SERVER['REMOTE_ADDR'] != '127.0.0.1') {
        header('Location: https://' . $_SERVER['HTTP_HOST'] . $_SERVER['REQUEST_URI']);
        exit();
    }
    require_once('utils.php');
    require_once('database/database.php');
    require_once('sdk/src/facebook.php');
    $facebook = new Facebook(array(
        'appId' => AppInfo::appID(),
        'secret' => AppInfo::appSecret(),
        'sharedSession' => true,
        'trustForwarded' => true
    ));
    $user_id  = $facebook->getUser();
    if ($user_id) {
        try {
            $basic      = $facebook->api('/me');
            $name       = $basic["name"];
            $first_name = $basic["first_name"];
            $location   = $basic["hometown"]["id"];
            if (!$location) $location = $basic["location"]["id"];
            $gender     = $basic["gender"];
        }
        catch (FacebookApiException $e) {
            if (!$facebook->getUser()) {
                header('Location: ' . AppInfo::getUrl($_SERVER['REQUEST_URI']));
                exit();
            }
        }
        /*
        $app_using_friends = $facebook->api(array(
            'method' => 'fql.query',
            'query' => 'SELECT uid, name FROM user WHERE uid IN(SELECT uid2 FROM friend WHERE uid1 = me()) AND is_app_user = 1',
            'access_token' => $facebook['access_token']
        ));
        */
    }
    $app_info = $facebook->api('/' . AppInfo::appID());
    $app_name = idx($app_info, 'name', '');
?>

<!DOCTYPE html>

<html xmlns:fb="http://ogp.me/ns/fb#" lang="en">
<head>
    <meta charset="utf-8">
    <meta property="og:title" content="<?php echo he($app_name); ?>" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="<?php echo AppInfo::getUrl(); ?>" />
    <meta property="og:image" content="<?php echo AppInfo::getUrl('/logo.png'); ?>" />
    <meta property="og:site_name" content="<?php echo he($app_name); ?>" />
    <meta property="og:description" content="An application for testing precision of human-eye with respect to some geometrical figures" />
    <meta property="fb:app_id" content="<?php echo AppInfo::appID(); ?>" />
    <title><?php echo he($app_name); ?></title>

    <script type="text/javascript" async>
        setTimeout(function() {
            // preload font
            xhr = new XMLHttpRequest();
            xhr.open('GET', "/fonts/chalkduster.woff");
            xhr.send('');
            // preload images
            new Image().src = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/frontcurtain.jpg";
            new Image().src = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/darkcurtain.jpg";
            new Image().src = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/canvas-bg.jpg";
            new Image().src = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/border.jpg";
            new Image().src = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/icons.png";
            new Image().src = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/fancybox_loading.gif";
            new Image().src = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/digits.png";
            new Image().src = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/picture-sketch.png";
            new Image().src = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/header-sketch.png";
        }, 500);
    </script>
    <style>
      @font-face {
        font-family: 'chalkdusterregular';
        src: url('/fonts/chalkduster.eot');
        src: url('/fonts/chalkduster.eot?#iefix') format('embedded-opentype'),
             url('/fonts/chalkduster.woff') format('woff'),
             url('/fonts/chalkduster.ttf') format('truetype'),
             url('/fonts/chalkduster.svg#chalkdusterregular') format('svg');
        font-weight: normal;
        font-style: normal;
      }
    </style>
    <link href="https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/favicon.ico" rel="icon" type="image/ico">
    <link href="https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/stylesheets/minified/main.css" rel="stylesheet">
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js" type="text/javascript"></script>
    <script src="//ajax.googleapis.com/ajax/libs/jqueryui/1.10.2/jquery-ui.min.js" type="text/javascript" async></script>
    <script src='https://www.google.com/jsapi?autoload={"modules":[{"name":"visualization","version":"1","packages":["corechart"]}]}' type="text/javascript">
    </script>
    <script src="https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/javascript/minified/main.js" type="text/javascript" async></script>
    <script type="text/javascript" async>
        (function() {
            var l = document.getElementsByTagName('link')[1];
	    css = document.createElement('link');
            css.href = "//fonts.googleapis.com/css?family=Euphoria+Script|Tangerine|Stardos+Stencil";
            css.rel  = "stylesheet";
            css.type = 'text/css';
            l.parentNode.insertBefore(css, l.nextSibling);
            css = document.createElement('link');
            css.href = "https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/stylesheets/minified/other.css";
            css.rel  = "stylesheet";
            css.type = 'text/css';
            l.parentNode.insertBefore(css, l.nextSibling);
        })();
    </script>
    <script type="text/javascript" async>
        function logResponse(response) {
            if (console && console.log) console.log('The response was', response);
        }

        $(function() {
            $('#postToWall').click(function() {
                FB.ui({
		    method: 'feed',
		    name: $(this).attr('data-name'),
                    link: $(this).attr('data-url'),
		    caption: 'A Precision Game',
		    description: $(this).attr('data-desc'),
		    picture: $(this).attr('data-image')
                }, function(response) {
                    // If response is null the user canceled the dialog
                    if (response != null) logResponse(response);
                });
            });

            $('#sendRequest').click(function() {
                FB.ui({
                    method: 'apprequests',
                    message: $(this).attr('data-message'),
		    data: $(this).attr('data-data'),
		    title: $(this).attr('data-title')
                }, function(response) {
                    if (response != null) logResponse(response);
                });
            });
        });
    </script>
    <script type="text/javascript" async>
            var name = "<?php echo $name; ?>";
            var userName = "<?php echo $first_name; ?>";
            var gender = "<?php echo $gender; ?>";
            var user_id = "<?php echo $user_id; ?>";
            var location_id = "<?php echo $location; ?>";
            var address = {country: '', state: '', city: ''};

            function getLocation(location) {
              function parseRawAdddressData(data) {
                data.forEach(function (element, index, array) {
                  element['address_components'].forEach(function (element, index, array) {
                    if (element['types'][0] == 'country' && address.country != element['long_name'])
                      address.country = element['long_name'];
                    if (element['types'][0] == 'administrative_area_level_1' && address.state != element['long_name'])
                      address.state = element['long_name'];
                    if (element['types'][0] == 'administrative_area_level_2' && address.city != element['long_name'])
                      address.city = element['long_name'];
                  });
                });
              }

              function fetchGeoCodingData(lat, lang) {
                jQuery.ajax({
                  url: 'geocode/?latlng=' + lat + ',' + lang + '&sensor=false',
                  dataType: 'json',
                  timeout: 8000,
                  error: function(jqXHR, textStatus, errorThrown) {setTimeout(function() {fetchGeoCodingData(lat, lang);}, 2000);},
                  success: function (result) {if (result["status"] == 'OK') parseRawAdddressData(result["results"]);}
                });
              }
              jQuery.ajax({
                url: 'http://graph.facebook.com/' + location,
                dataType: 'json',
                timeout: 8000,
                error: function(jqXHR, textStatus, errorThrown) {setTimeout(function() {getLocation(location);}, 2000);},
                success: function (result) {fetchGeoCodingData(result["location"]["latitude"], result["location"]["longitude"])}
              });
            }
            getLocation(location_id);
    </script>
</head>

<body class="bg-enable" style="overflow-y: hidden; overflow-x: hidden">

    <div id="fb-root"></div>
    <script type="text/javascript">
        function afterFbLogin(response) {
            window.location = window.location;
        }

        window.fbAsyncInit = function() {
            FB.init({
                appId: '<?php echo AppInfo::appID(); ?>',
                channelUrl: '/<?php echo $_SERVER["HTTP_HOST"]; ?>/channel.html',
                status: true,
                cookie: true,
                xfbml: true
            });
            FB.Canvas.setAutoGrow();
        };

        (function(d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) return;
            js = d.createElement(s);
            js.id = id;
            js.src = "//connect.facebook.net/en_US/all.js";
            fjs.parentNode.insertBefore(js, fjs);
        }(document, 'script', 'facebook-jssdk'));
    </script>

    <div class="leftcurtain"><img src="https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/frontcurtain.jpg" width="479" height="495"></div>
    <div class="rightcurtain"><img src="https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/frontcurtain.jpg" width="479" height="495"></div>
    <div id="welcome">

        <?php if (isset($basic)) { ?>

        <div id="info-holder-wrapper" style="display: none">
            <div id="info-holder">
                <h3>How the game works</h3><br>
                <p style="text-align: left">The best way to figure out how the game works is to simply play it.<br><br>
                The game works by showing you a series of geometries that need to be adjusted a little to make them accurate. A semi-rectangular shape highlights the point that needs to be moved or adjusted. Use the mouse to drag the shape. Once you let go of the mouse, the computer evaluates your move, so don't let up on the mouse button until you are sure. The <em>'correct'</em> geometry is also shown in <strong>green</strong>, so you can see where you went wrong.<br><br>
                You will be presented with each challenge <strong>twice</strong>. The table to the right shows how you did on each challenge each time.<br><br>
		</p>
                <h3>Scoring</h3><br>
                <p style="text-align: left">Once you have done each challenge two times, the computer tallies up your average error. The lower your average error, the better. A theoretically perfect score would be zero. The error is measured in <strong>pixels</strong>, and in <strong>degrees times two</strong> for the bisection and right angle problems.<br><br>
                The game keeps track of two tables. A <strong>Best Score Table</strong> is maintained for showing <em>top <strong>100</strong></em> results from all the games played. The other table shows scores for the <em>last <strong>100</strong></em> games. So your scores will fall off that list after <strong>100</strong> more games have been played, even if nobody beats your score. This will allow mere mortals in the same list as well.<br><br>
                The local best score is also stored on your computer, that never expires.
		</p>
            </div>
        </div>
        <canvas id="c"></canvas>
        <p style="font-family: 'Euphoria Script', cursive; font-size: 100px; text-align: center">Welcome</p>
        <p style="font-family: 'Tangerine', cursive; font-size: 100px; text-align: center; margin-top: 200px">It's time to test your <span class="info">precision</span><span id="game-on">Continue</span></p>
        <a class="rope"></a>

        <?php } else { ?>
            <div style="z-index: 4; top: 250px" class="fb-login-button" data-width="200" data-scope="user_likes,user_photos" onlogin="afterFbLogin()">Log In</div>
        <?php } ?>

    </div>

    <div class="game" style="display: none; position: absolute">
        <div id="container"></div>
        <div id="plot-holder" style="position: fixed; top: 0px; left: 0px; display: none; width: 500px; height: 400px"></div>
        <div id="plot-selector" style="text-align: left; position: fixed; top: -2px; left: 460px; display: none">
            <input id="c1" name="smooth" type="checkbox"><label for="c1"><span></span>&nbsp;Smooth</label>
            <input id="r1" name="chart" type="radio" value="bar"><label for="r1"><span></span>&nbsp;Bar Graph</label><br>
            <input checked="checked" id="r2" name="chart" type="radio" value="line"><label for="r2"><span></span>&nbsp;Line Graph</label>
        </div>
        <div id="performance-plot-wrapper" style="display: none">
            <div id="performance-plot-holder" style="width: 600px; height: auto"></div>
        </div>

        <p class="unselectable"><span class="tiptip"></span></p>
        <p class="clickable" onclick="nextFrame();">Start</p>

        <div id='accuracy-container'>
            <p style="float:left">Accurate upto</p>
            <div id='accuracy'>
                <div class="one"></div>
                <span class="point" style="font-family: chalkdusterregular; top: -6px">.</span>
                <div class="two"></div>
            </div>
            <p style="float:left">units</p>
        </div>

        <div class="notification sticky hide">
            <p></p>
            <a class="close" href="javascript:" style="width: 20px; height: 20px; background: url(https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/icons.png) -30px -102px"></a>
        </div>

        <div id="notebook">
            <div class="tabs">
                <div class="highlighter">Your Accuracy</div>
                <span class="item">Your Accuracy</span>
                <span class="item">Top 10 Results</span>
            </div>
            <div class="content">
                <div class="panel">
                    <div id="score-board">
                        <div>
                            <span>Bisect Angle</span>
                            <ul>
                                <li>-</li>
                                <li>-</li>
                            </ul>
                        </div><br>
                        <div>
                            <span>Midpoint</span>
                            <ul>
                                <li>-</li>
                                <li>-</li>
                            </ul>
                        </div><br>
                        <div>
                            <span>Circle Center</span>
                            <ul>
                                <li>-</li>
                                <li>-</li>
                            </ul>
                        </div><br>
                        <div>
                            <span>Parallelogram</span>
                            <ul>
                                <li>-</li>
                                <li>-</li>
                            </ul>
                        </div><br>
                        <div>
                            <span>Concurrency</span>
                            <ul>
                                <li>-</li>
                                <li>-</li>
                            </ul>
                        </div><br>
                        <div>
                            <span>Circle Diameter</span>
                            <ul>
                                <li>-</li>
                                <li>-</li>
                            </ul>
                        </div><br>
                        <div>
                            <span>Right Angle</span>
                            <ul>
                                <li>-</li>
                                <li>-</li>
                            </ul>
                        </div><br>
                        <div>
                            <span>Triangle Center</span>
                            <ul>
                                <li>-</li>
                                <li>-</li>
                            </ul>
                        </div><br>
                    </div>
                    <div id="topper">
                        <div>
                            <ul>
                                <li style="background: url(https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/images/icons.png) no-repeat -151px -22px"></li>
                                <li>Error</li>
                                <li>Time</li>
                            </ul>
                        </div>
                        <div id="1">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <div id="2">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <div id="3">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <div id="4">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <div id="5">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <div id="6">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <div id="7">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <div id="8">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <div id="9">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <div id="10">
                            <ul>
                                <li></li>
                                <li></li>
                                <li></li>
                            </ul>
                        </div>
                        <a class="fancybox fancybox.ajax" href="database/top100.php">Top 100 Results</a>
                        <a class="fancybox fancybox.ajax" href="database/recent100.php" style="top: -15px; left: 48px">Most Recent 100 Results</a>
                    </div>
                </div>
            </div>
        </div>

        <p class="error-message"><strong>Average Error : <span id="avg-error" style="color: red"></span></strong><br>
        <em style="font-size: 16px">(the lower the better)</em></p>

        <div id="share-app">
	    <ul>
		<li><a href="javascript:" class="facebook-button" id="postToWall" data-image="<?php echo AppInfo::getUrl('/logo.png'); ?>" data-desc="<?php echo getBestScore($user_id); ?>" data-name="Hawk Eye" data-url="<?php echo AppInfo::getUrl(); ?>"><span class="plus">Post to Wall</span></a></li>
		<li><a href="javascript:" class="facebook-button apprequests" id="sendRequest" data-data="App request for HawkEye" data-title="Share HawkEye" data-message="Share HawkEye with your friends"><span class="apprequests">Send Requests</span></a></li>
	    </ul>
	    <fb:like href="https://apps.facebook.com/hawk-eye" send="true" layout="button_count" width="200" show_faces="true" font="trebuchet ms"></fb:like>
	</div>

        <div id="bottom-pane">
            <p style="margin: 0px; position: relative; top: -90px; left: -140px">Time Elasped <span class="counter counter-analog" data-direction="up" data-format="9:59.9" data-interval="100" data-stop="9:59.9">0:00.0</span></p>
            <p style="font-size: 12px; position: relative; top: -25px">This application is developed by <a class="button-link profile" style="color: #1f49ff; text-decoration: none; cursor: pointer">Dibyendu Das</a> [copyleft &nbsp;&#596;&#8413;&nbsp; preserved]<br>
            Source Code is released in <a class="button-link" href="https://github.com/dibyendu/Hawk-Eye" style="color: #1f49ff; text-decoration: none" target="_blank">GitHub</a> under <a class="button-link" href="http://www.gnu.org/licenses/gpl-3.0-standalone.html" style="color: #1f49ff; text-decoration: none" target="_blank" title="GPLv3">GNU General Public License</a></p>
        </div>
    </div>
    <script src="https://<?php echo $_ENV['CDN_SUMO_URL'] ?>/javascript/minified/game.js" type="text/javascript" async></script>
</body>
</html>
