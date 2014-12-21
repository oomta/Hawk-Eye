var graph_data = [];

function postData(name, gender, id, address, error, time) {
    jQuery.ajax({
        url: 'database/update.php',
        type: 'POST',
        timeout: 20000,
        data: {
            name: name,
            gender: gender,
            id: id,
            city: address.city,
            state: address.state,
            country: address.country,
            error: error,
            time: time
        },
        error: function (jqXHR, textStatus, errorThrown) {
            setTimeout(function () {
                postData(name, gender, id, address, error, time);
            }, 500);
        },
        success: function (message) {
            jQuery('.notification p').html("<span style='color: #111'>Thank you&nbsp;&nbsp;<span class='blink' style='color: #000'>" + userName + "</span>&nbsp;&nbsp;for trying. Your score has been submitted successfully.</span>");
            jQuery('.notification.sticky').notify();
            jQuery(".blink").tipTip({
                delay: 200,
                defaultPosition: "bottom",
                keepAlive: true,
                content: "Your stats are being fetched ..."
            });
            registerSuccessfulCompletion(id, error, time);
            fetchTop10();
            if (localStorage.HawkEyeScore) localStorage.HawkEyeScore = (parseFloat(localStorage.HawkEyeScore) > parseFloat(error)) ? parseFloat(error) : localStorage.HawkEyeScore;
            else localStorage.HawkEyeScore = parseFloat(error);
            var img = jQuery("<img>").attr({
                'src': "https://chart.googleapis.com/chart?chst=d_fnote_title&chld=pinned_c|1|1269A0|h|" + localStorage.HawkEyeScore + "|is the best score|stored in|this browser",
            	'width': '128px',
		'height': '141px'
	    }).load(

            function () {
                if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) alert('broken image!');
                else {
                    jQuery("#score-board img").remove();
                    jQuery("#score-board").append(img);
                }
            });
        }
    });
}

function registerGameInit(name, gender, id, address) {
    jQuery.ajax({
        url: 'database/registerInit.php',
        type: 'POST',
        timeout: 20000,
        data: {
            name: name,
            gender: gender,
            id: id,
            city: address.city,
            state: address.state,
            country: address.country
        },
        error: function (jqXHR, textStatus, errorThrown) {
            setTimeout(function () {
                registerGameInit(name, gender, id, address);
            }, 500);
        }
    });
}

function registerSuccessfulCompletion(id, error, time) {
    jQuery.ajax({
        url: 'database/registerCompletion.php',
        type: 'POST',
        timeout: 20000,
        data: {
            error: error,
            time: time,
            id: id
        },
        error: function (jqXHR, textStatus, errorThrown) {
            setTimeout(function () {
                registerSuccessfulCompletion(id, error, time);
            }, 500);
        },
        success: function (message) {
            var obj = jQuery.parseJSON(message);
            var successLog = [],
                content;
	    jQuery('#postToWall').attr('data-desc', "My best score is <b>" + obj['best-score-error'].toString() + "</b>, in <b>" + obj['best-score-time'].toString() + "</b> sec. Scored on <i>" + obj['best-score-date'] + "</i>");
            for (var i = 0; i < obj['logs'].length; i++) if ('fdate' in obj['logs'][i]) successLog.push(obj['logs'][i]);
            content = "You've successfully completed <span style='color: yellow'><b>" + successLog.length + "</b></span> time" + (successLog.length > 1 ? "s." : ".");
            content += "<div style='height: 300px; overflow-y: auto'><center><br><table border='1'><tr><th>Date</th><th>Error</th><th>Time</th></tr>";
            for (var i = successLog.length - 1; i >= 0; i--) content += "<tr  style='text-align: center'><td>" + new Date((successLog[i]['fdate']['sec'] * 1000000 + successLog[i]['fdate']['usec']) / 1000).toLocaleString().replace(new RegExp('[A-z]+'), '') + "</td><td><span style='color: yellow; text-align: center'>" + successLog[i]['error'] + "</span></td><td><span style='color: yellow; text-align: center'>" + successLog[i]['time'] + "</span></td></tr>";
            content += "</table></center></div><br><p style='text-align: left'><a class='fancy-plot' style='color: yellow; text-decoration: none' href='#performance-plot-holder'>Visualize your performance</a></p>";
            jQuery(".blink").tipTip({
                delay: 200,
                defaultPosition: "bottom",
                keepAlive: true,
                content: content
            });
            var performance_plot_html;
            jQuery(".fancy-plot").fancybox({
                beforeLoad: function () {
                    performance_plot_html = jQuery("#performance-plot-wrapper").html();
                },
                beforeShow: function () {
                    performanceGraph(successLog);
                    jQuery(".fancybox-heading").html("<span style='color: white'>" + userName + "'s Performance</span>");
                    jQuery(".fancybox-header").css('display', 'none');
                },
                afterShow: function () {
                    jQuery(".fancybox-close").css('top', '+=46');
                },
                afterClose: function () {
                    jQuery("#performance-plot-wrapper").html(performance_plot_html);
                }
            });
        }
    });
}

function loadImage(index, id, link, error, time, name, sex, date, address) {
    var img = jQuery("<img>").attr({
        'src': 'https://graph.facebook.com/' + id + '/picture?width=38&height=38',
        'width': '38px',
        'height': '38px'
    }).load(
    function () {
        if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) alert('broken image!');
        else {
            jQuery("#topper #" + (index + 1) + " li:eq(0)").html("<a href='" + link + "' target='_blank'></a>");
            jQuery("#topper #" + (index + 1) + " li:eq(0) a").append(img);
            jQuery("#topper #" + (index + 1) + " li:eq(1)").html(error);
            jQuery("#topper #" + (index + 1) + " li:eq(2)").html(time);
            var tooltip = '';
            var pos = 'left';
            if (index == 0) {
                tooltip += "<div class='medal first'></div><br/>";
                pos = "bottom";
            } else if (index == 1) tooltip += "<div class='medal second'></div><br/>";
            else if (index == 2) tooltip += "<div class='medal third'></div><br/>";
            tooltip += "<div style='text-align: left'><span style='color: yellow'>Name : </span>" + name + "<br/>";
            if (sex) tooltip += "<span style='color: yellow'>Gender : </span>" + (sex == 'male' ? '♂' : '♀') + '<br/>';
            var loc = '';
            if (address.city) loc += address.city + ", ";
            if (address.state) loc += address.state + ", ";
            if (address.country) loc += address.country;
            tooltip += "<span style='color: yellow'>From : </span>" + loc + "<br/>";
            tooltip += "<span style='color: yellow'>Scored on : </span>" + date + "</div>";
            img.tipTip({
                defaultPosition: pos,
                content: tooltip
            });
        }
    });
}

function fetchTop10() {
    jQuery.ajax({
        url: 'database/top10.php',
        dataType: 'json',
        timeout: 30000,
        error: function (jqXHR, textStatus, errorThrown) {
            setTimeout(fetchTop10, 500);
        },
        success: function (result) {
            for (var i = 0; i < result.length; i++) loadImage(i, result[i]["_id"], "https://www.facebook.com/" + result[i]["_id"], result[i]["error"], result[i]["time"], result[i]["name"], result[i]["sex"], result[i]["date"], result[i]["address"]);
        }
    });
}

function fetchErrorDistribution() {
    jQuery.ajax({
        url: 'database/error.php',
        dataType: 'json',
        timeout: 20000,
        error: function (jqXHR, textStatus, errorThrown) {
            setTimeout(fetchErrorDistribution, 500);
        },
        success: function (result) {
            for (var i = 0; i < result.length; i++) graph_data.push([result[i]["error"], result[i]["count"]]);
        }
    });
}
jQuery(document).ready(

function () {

if (localStorage.HawkEyeScore) {
		var img = jQuery("<img>").attr({'src': "https://chart.googleapis.com/chart?chst=d_fnote_title&chld=pinned_c|1|1269A0|h|" + localStorage.HawkEyeScore + "|is the best score|stored in|this browser", 'width': '128px', 'height': '141px'}).load(function () {if (!this.complete || typeof this.naturalWidth == "undefined" || this.naturalWidth == 0) alert('broken image!');else jQuery("#score-board").append(img);});
		}

                displayName(userName);

		jQuery('.fancybox').fancybox({type: 'ajax', dataType: 'text', headers: { 'X-fancyBox': true }, maxWidth: 800, maxHeight: 600, fitToView: false, width: '28%', height: '70%', autoSize: false, closeBtn : true});

		jQuery(".profile").tipTip({delay: 200, defaultPosition: "top", keepAlive: true, content: "<div style='height: 32px; display: block'><a class='social-icons fb' href='https://www.facebook.com/dibyendu2008' target='_blank' title='Dibyendu Das on Facebook' alt='Dibyendu Das Facebook Icon'></a><a class='social-icons gp' href='https://plus.google.com/u/0/102672758860666735108' target='_blank' title='Dibyendu Das on Google+' alt='Dibyendu Das Google+ Icon'></a></div>"});

    jQuery('.highlighter').css({left:jQuery('span.item:first').position()['left']});
		
		jQuery('.item').mouseover(function () {
			//scroll the header-box to current item position
			var text = jQuery(this).text();
			jQuery('.highlighter').stop().animate({left:jQuery(this).position()['left']}, 200, function() {jQuery('.highlighter').html(text);});
			
			//scroll the panel to the correct content
			jQuery('.panel').stop().animate({left:jQuery(this).position()['left'] * (-2)}, {duration:200});
		});

    var info_data = jQuery("#info-holder-wrapper").html();;
    jQuery('.info').click(
    function () {
        jQuery.fancybox({
	    width: '70%',
	    height: '60%',
	    autoSize: false,
            content: info_data,
            beforeShow: function () {
                jQuery(".fancybox-heading").html("<span style='color: white'>About HawkEye</span>");
                jQuery(".fancybox-header").css('display', 'none');
            },
            afterShow: function () {
                jQuery(".fancybox-close").css('top', '+=46');
            }
        });
    });

    jQuery('#game-on').click(
    function () {
        registerGameInit(name, gender, user_id, address);
        fetchTop10();
        fetchErrorDistribution();
        jQuery('#game-on').animate({
            opacity: 0
        }, 1000, function () {
            jQuery(".leftcurtain").stop().animate({
                left: '-60px'
            }, 2500);
            jQuery(".rightcurtain").stop().animate({
                right: '-60px'
            }, 2500);
            jQuery(".rope").stop().animate({
                top: '-320px'
            }, 2500, function () {
                jQuery('#welcome').hide("puff", {}, function () {
                    jQuery("body").removeClass('bg-enable').addClass('bg-disable');
                    jQuery('.game').show("fade", {}, function () {
                        setTimeout("startFrame(userName)", 500);
                        jQuery('.fb_iframe_widget').css({
                            "position": "fixed",
                            "top": "10px",
                            "left": "10px"
                        });
                        jQuery('.fb_iframe_widget span').css({
                            "width": "140px",
                            "height": "20px"
                        });
                        jQuery('.fb_iframe_widget span iframe').css({
                            "width": "140px",
                            "height": "20px"
                        });
                    }, 2000);
                }, 2000);
            });
        });
    });
    $curtainopen = false;
    $(".rope").click(function () {
        $(this).blur();
        if ($curtainopen == false) {
            $(this).stop().animate({
                top: '0px'
            }, {
                queue: false,
                duration: 350,
                easing: 'easeOutBounce'
            });
            $(".leftcurtain").stop().animate({
                width: '60px'
            }, 2000);
            $(".rightcurtain").stop().animate({
                width: '60px'
            }, 2000);
            $curtainopen = true;
        } else {
            $(this).stop().animate({
                top: '-40px'
            }, {
                queue: false,
                duration: 350,
                easing: 'easeOutBounce'
            });
            $(".leftcurtain").stop().animate({
                width: '50%'
            }, 2000);
            $(".rightcurtain").stop().animate({
                width: '51%'
            }, 2000);
            $curtainopen = false;
        }
        return false;
    });
    jQuery("input[name=chart]").change(

    function () {
        var val = jQuery("input[name=chart]:checked").val();
        if (val == "line") {
            graph.setChartType("LineChart");
            graph.draw();
            jQuery("#plot-selector input[type='checkbox'] + label").show();
        } else {
            graph.setChartType("ColumnChart");
            graph.draw();
            jQuery("#plot-selector input[type='checkbox'] + label").hide();
        }
    });
    jQuery("input[name=smooth]").change(function () {
        if (jQuery("input[name=smooth]").is(":checked")) {
            graph.setOption('curveType', 'function');
            graph.setOption('pointSize', '0');
            graph.draw();
        } else {
            graph.setOption('curveType', 'none');
            graph.setOption('pointSize', '3');
            graph.draw();
        }
    });
});

function blinkInfo() {
    jQuery('.info').toggleClass('no-shadow');
    jQuery('.blink').toggleClass('no-shadow');
    setTimeout(blinkInfo, 1000);
}
setTimeout(blinkInfo, 1000);
jQuery(function () {
    jQuery('.counter').counter();
    jQuery('.counter').counter('stop');
    jQuery('.one').odoTicker({
        number: 0
    });
    jQuery('.two').odoTicker({
        number: 0
    });
});

function performanceGraph(records) {
    var data = new google.visualization.DataTable();
    data.addColumn('date', 'Date');
    data.addColumn('number', 'Error');
    data.addColumn({
        type: 'string',
        role: 'tooltip',
        p: {
            html: true
        }
    });
    for (var i = 0; i < records.length; i++) data.addRow([
            new Date((records[i]['fdate']['sec'] * 1000000 + records[i]['fdate']['usec']) / 1000), records[i]['error'], '<div style="text-align: left"><b>Error: <span style="color: blue">' + records[i]['error'] + '</span><br/>Time: <span style="color: blue">' + records[i]['time'] + '</span><br/>Date: <span style="color: blue">' + new Date(records[i]['fdate']['sec'] * 1000 + records[i]['fdate']['usec']).toLocaleString() + '</span></b></div>'
        ]);
    var option = {
        width: 580,
        height: 440,
        pointSize: 3,
        lineWidth: 2,
        colors: ['#55C1D0'],
        backgroundColor: {
            fill: 'transparent',
            stroke: '#fff',
            strokeWidth: 1
        },
        legend: {
            position: 'none'
        },
        chartArea: {
            left: 44,
            top: 10,
            width: '500',
            height: '400'
        },
        tooltip: {
            isHtml: true
        },
        vAxis: {
            textStyle: {
                color: '#000',
                fontName: 'Stardos Stencil',
                fontSize: 13
            },
            textPosition: 'out',
            title: 'Error',
            titleTextStyle: {
                fontName: 'Stardos Stencil',
                fontSize: 14
            }
        },
        hAxis: {
            slantedText: false,
	    maxAlternation: 2,
            textStyle: {
                color: '#000',
                fontName: 'Stardos Stencil',
                fontSize: 10
            },
            textPosition: 'out',
            title: 'Time',
            titleTextStyle: {
                fontName: 'Stardos Stencil',
                fontSize: 14
            }
        }
    }
    var chart = new google.visualization.ChartWrapper({
        chartType: 'AreaChart',
        dataTable: data,
        options: option,
        containerId: 'performance-plot-holder'
    });
    chart.draw(data, option);
}

function showGraph(error) {
    var data = new google.visualization.DataTable();
    data.addColumn('number', 'Percent');
    data.addColumn('number', 'Error');
    data.addColumn({
        type: 'string',
        role: 'annotation'
    });
    data.addColumn({
        type: 'string',
        role: 'annotationText',
        p: {
            html: true
        }
    });
    data.addColumn({
        type: 'string',
        role: 'tooltip',
        p: {
            html: true
        }
    });
    var err = parseFloat((error - 0.01).toFixed(1));
    var total = 0,
        ahead = 0;
    var selection = 0;
    for (var i = 0; i < graph_data.length; i++) {
        if (graph_data[i][0] < err) ahead += parseInt(graph_data[i][1]);
        total += parseInt(graph_data[i][1]);
    }
    for (var i = 0; i < graph_data.length; i++) {
        if (graph_data[i][0] == err) {
            selection = i;
            data.addRow([
                graph_data[i][0], graph_data[i][1] / total, userName, '&nbsp;&nbsp;<span style="display: block; height: 14px; font-size: 14px">Rank : <b>' + (ahead + 1) + '</b> and <a href="http://en.wikipedia.org/wiki/Percentile_rank" target="_blank">Percentile</a> : <b>' + ((total - ahead - 0.5 * graph_data[i][1]) * 100 / total).toFixed(2) + "%</b></span>&nbsp;&nbsp;", '&nbsp;&nbsp;<span style="font-size: 13px; color: #2239dc"><b>' + (graph_data[i][1] * 100 / total).toFixed(2) + '%</b> people [<b>' + graph_data[i][1] + '</b>] with error <b>' + graph_data[i][0] + '</b></span>&nbsp;&nbsp;'
            ]);
        } else data.addRow([
                graph_data[i][0], graph_data[i][1] / total, null, null, '&nbsp;&nbsp;<span style="font-size: 13px; color: #2239dc"><b>' + (graph_data[i][1] * 100 / total).toFixed(2) + '%</b> people [<b>' + graph_data[i][1] + '</b>] with error <b>' + graph_data[i][0] + '</b></span>&nbsp;&nbsp;'
            ]);
    }
    var option = {
        curveType: "none",
        width: 580,
        height: 480,
        pointSize: 3,
        lineWidth: 2,
        bar: {
            groupWidth: "80%"
        },
        colors: ['#55C1D0'],
        backgroundColor: {
            fill: 'transparent',
            stroke: '#fff',
            strokeWidth: 1
        },
        legend: {
            position: 'none'
        },
        chartArea: {
            left: 40,
            top: 40,
            width: "500",
            height: "400"
        },
        tooltip: {
            isHtml: true
        },
        vAxis: {
            format: '#%',
            //maxValue: 1,
            minValue: 0,
            gridlines: {
                //count: 6,
                color: '#ccc'
            },
            minorGridlines: {
                count: 0
            },
            textStyle: {
                color: '#000',
                fontName: 'Stardos Stencil',
                fontSize: 13
            },
            textPosition: 'out'
        },
        hAxis: {
            slantedTextAngle: 60,
            gridlines: {
                color: '#ccc'
            },
            minorGridlines: {
                count: 0
            },
	    title: 'Error',
            textStyle: {
                color: '#000',
                fontName: 'Stardos Stencil',
                fontSize: 12
            },
            textPosition: 'out'
        }
    }
    var chart = new google.visualization.ChartWrapper({
        chartType: 'LineChart',
        dataTable: data,
        options: option,
        containerId: 'plot-holder'
    });
    google.visualization.events.addListener(chart, 'ready', onReady);

    function onReady() {
        chart.getChart().setSelection([{
                row: selection,
                column: null
            }
        ]);
        google.visualization.events.addListener(chart, 'select', fixedSelection);
        google.visualization.events.addListener(chart.getChart(), 'onmouseover', handleMouseOver);
        google.visualization.events.addListener(chart.getChart(), 'onmouseout', handleMouseOut);
    }

    function handleMouseOver(e) {
        jQuery('#plot-holder').css('z-index', '1');
    }

    function handleMouseOut(e) {
        jQuery('#plot-holder').css('z-index', '0');
    }

    function fixedSelection(e) {
        chart.getChart().setSelection([{
                row: selection,
                column: null
            }
        ]);
    }
    chart.draw(data, option);
    return chart;
}

(function ($) {
    $.fn.extend({
        notify: function (options) {
            var settings = $.extend({ type: 'sticky', speed: 500, onDemandButtonHeight: 35 }, options);
            return this.each(function () {
                var wrapper = $(this);
                var ondemandBtn = $('.ondemand-button');
                var dh = -35;
                var w = wrapper.outerWidth() - ondemandBtn.outerWidth();
                ondemandBtn.css('left', w).css('margin-top',  dh + "px" );
                var h = -wrapper.outerHeight();
                wrapper.addClass(settings.type).css('margin-top', h).addClass('visible').removeClass('hide');
                wrapper.stop(true, false).animate({ marginTop: 0 }, settings.speed);    
                var closeBtn = $('.close', wrapper);
                closeBtn.click(function () {
                    wrapper.stop(true, false).animate({ marginTop: h }, settings.speed, function () {
                        wrapper.removeClass('visible').addClass('hide');
                    });
                });
            });	
        }
    });
})(jQuery);
