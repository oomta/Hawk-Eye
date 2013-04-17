var frames = [bisectFrame, midPointFrame, circleFrame, rectFrame, convergeFrame, diaFrame, rightFrame, triFrame];
var frameIndex = 0;
var nRound = 2;
var graph = null;

function updateGraphData(error) {
    var exists = false;
    var i;
    var err = parseFloat((error - 0.01).toFixed(1));
    for (i = 0; i < graph_data.length; i++) {
        if (graph_data[i][0] == err) {
            graph_data[i][1] += parseInt(1);
            exists = true;
            break;
        }
        if (graph_data[i][0] > err) break;
    }

    if (!exists) graph_data.splice(i, 0, [err, 1]);
}

function nextFrame() {
    if (activeLayer) activeLayer.hide();
    stage.clear();
    if (graph) {
        jQuery('#plot-holder').css('display', 'none');
        jQuery('#plot-selector').css('display', 'none');
        graph.getChart().clearChart();
        jQuery('#accuracy-container').show();
        jQuery('#share-app ul').animate({width: 'toggle'}, 1000);
        graph = '';
        jQuery('.counter').counter('reset');
        jQuery('#avg-error').html("");
        jQuery('#score-board li').html('-');
        globalError = parseFloat(0.0);
        count = parseInt(0);
        registerGameInit(name, gender, user_id, address);
    }
    if (!nRound) {
        endFrame(userName, globalError / (frames.length * 2.0));
        var time = parseInt(jQuery('.counter .part0 .digit').html()) * 60 + parseInt(jQuery('.counter .part2 .digit').html()) * 10 + parseInt(jQuery('.counter .part2 .digit').next().html()) + parseInt(jQuery('.counter .part4 .digit').html()) / 10;
        postData(name, gender, user_id, address, jQuery('#avg-error').html(), time);
        updateGraphData(globalError / (frames.length * 2.0));
        jQuery('.clickable').html('Show Graph');
        jQuery('#accuracy .one').odoTicker({
            number: 0
        });
        jQuery('#accuracy .two').odoTicker({
            number: 0
        });
        jQuery('.tiptip').html("");
        nRound -= 1;
        return;
    }
    if (nRound < 0) {
        jQuery('#plot-holder').css('display', 'block');
        jQuery('#plot-selector').css('display', 'block');
        graph = showGraph(globalError / (frames.length * 2.0));
        jQuery('#share-app ul').animate({width: 'toggle'}, 1000);
        jQuery('.clickable').html('Try Again');
        jQuery('.clickable').addClass('rotate');
        jQuery('.tiptip').html("Error Distribution Graph");
        jQuery(".tiptip").tipTip({
            defaultPosition: "bottom",
            content: "The horizontal axis represents the <i>Error</i> whereas the vertical one is showing the <i><b>%</b> of people</i>.<br>Hover over the plot to see individual details."
        });
        var left = 290 - jQuery('.tiptip').width() / 2;
        jQuery('.unselectable').css({
            "left": left
        });
        jQuery('#accuracy-container').hide();
        nRound = 1;
        frameIndex = 0;
        return;
    }
    jQuery('.clickable').hide("explode", {
        pieces: 8
    }, function () {
        jQuery('.clickable').html('Next');
        if (jQuery('.clickable').hasClass('rotate')) jQuery('.clickable').removeClass('rotate');
    }, 1400);
    frames[frameIndex](frameIndex * 2 + 2 - nRound);
    frameIndex += 1;
    frameIndex %= frames.length;
    if (!frameIndex) nRound -= 1;
}
