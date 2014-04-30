var frame = $('<div id="frame"></div>')
    .css({
	'position': 'fixed',
	'left': '0',
	'top': '0',
	'width': '100%',
	'height': '100%',
	'zIndex': '3',
	'overflow': 'hidden',
    });
var boom = $('<img id="boom">')
    .css({
	'position': 'absolute',
	'width': '100%',
	'left': '0%',
	'height': '4300%',
	'top': '0%'
    })
    .appendTo(frame);
$(function() { boom.attr('src', '/static/explosion.png') });

function explode(fallout) {
    $('body').append(frame);
    var f = 0;
    function next_frame() {
	boom.css('top', '-' + f + '00%');
	f++;
	if (f < 43)
	    setTimeout(next_frame, 120);
	else {
	    fallout();
	}
    }
    next_frame();
}
