var endFrame = function (name, error) {

    var layer = new Kinetic.Layer();
    activeLayer = layer;

    var minute = jQuery('.counter .part0 .digit').html();
    var second = parseInt(jQuery('.counter .part2 .digit').html()) * 10 + parseInt(jQuery('.counter .part2 .digit').next().html()) + parseInt(jQuery('.counter .part4 .digit').html()) / 10;

    var unitText = 'unit' + (error > 1 ? 's' : '');
    var minText = 'minute' + (parseInt(minute) > 1 ? 's' : '');
    var secText = 'second' + (second > 1 ? 's' : '');

    var text = new Kinetic.Text({
        x: 0,
        y: 60,
        text: "That's it\n\nYou ended up with an average accuracy of               " + unitText + " in\n   " + minText + "        " + secText + ".",
        fontSize: 20,
        fontFamily: 'chalkdusterregular',
        textFill: '#fff',
        width: 500,
        padding: 30,
        align: 'center',
        lineHeight: 2
    });

    var name = new Kinetic.Text({
        x: 0,
        y: 100,
        text: name + " !",
        fontSize: 20,
        fontFamily: 'chalkdusterregular',
        textFill: '#0f0',
        width: 500,
        padding: 30,
        align: 'center',
        lineHeight: 2
    });

    var error = new Kinetic.Text({
        x: 50,
        y: 222,
        text: (error + 0.0005).toFixed(3),
        fontSize: 20,
        fontFamily: 'chalkdusterregular',
        textFill: '#f00',
        width: 500,
        padding: 30,
        align: 'left'
    });

    var minuteText = new Kinetic.Text({
        x: 4,
        y: 258,
        text: minute,
        fontSize: 22,
        fontFamily: 'chalkdusterregular',
        textFill: '#ff0',
        width: 500,
        padding: 30,
        align: 'left'
    });

    var secondText = new Kinetic.Text({
        x: 190,
        y: 258,
        text: second,
        fontSize: 22,
        fontFamily: 'chalkdusterregular',
        textFill: '#ff0',
        width: 500,
        padding: 30,
        align: 'left'
    });

    layer.add(text);
    layer.add(name);
    layer.add(error);
    layer.add(minuteText);
    layer.add(secondText);
    stage.add(layer);

}
