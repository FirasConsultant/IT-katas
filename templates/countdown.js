elapsed = 0;

function countdown() {
    var time = rem_time - elapsed;
    var days = Math.floor(time / (3600 * 24));
    var secs = time % (3600 * 24);
    var t = new Date(secs * 1000);
    
    var cd = document.getElementById('countdown');
    if (cd) {
	cd.innerHTML = days + ' jours et ' + t.getUTCHours() + ':' +
            (t.getUTCMinutes() < 10 ? '0' : '') + 
            t.getUTCMinutes() + ':' +
            (t.getUTCSeconds() < 10 ? '0' : '') + 
            t.getUTCSeconds();
	
	elapsed += 1;
	setTimeout('countdown()', 1000);
    }
}

rem_time = {{ countdown.rem.days * 24 * 3600 + countdown.rem.seconds }};
