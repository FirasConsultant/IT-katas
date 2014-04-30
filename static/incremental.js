var incremental = {
    cursorBlink:        500,
    defaultSpeed:       150,
    defaultPauseBefore:   0,
    defaultPauseAfter:  400,
    defaultByLetter:      0,

    curIndex: -1,

    getElts : function() {
	this.elts = document.getElementsByClassName('incremental');
	for (var i = 0 ; i < this.elts.length ; i++)
	    this.elts[i].style.visibility = 'hidden';
    },

    getByIds : function(ids) {
	this.elts = [];
        var j = 0;
	for (var i in ids) {
	    this.elts[j] = document.getElementById(ids[i]);
	    this.elts[j].style.visibility = 'hidden';
            j++;
	}
    },

    prepare : function(next) {
	this.curIndex++;
	if (this.curIndex < this.elts.length) {
	    this.curElt = this.elts[this.curIndex];
	    this.speed = this.curElt.dataset.incrementalSpeed ||
		this.defaultSpeed;
	    this.pauseBefore =
		this.curElt.dataset.incrementalPauseBefore ||
		this.defaultPauseBefore;
	    this.pauseAfter =
		this.curElt.dataset.incrementalPauseAfter ||
		this.defaultPauseAfter;
	    this.byLetter = 
		this.curElt.dataset.incrementalByLetter !== undefined;

	    setTimeout(this.show.bind(this, next), this.pauseBefore);
	} else if (next) {
	    next();
	}
    },

    show : function(next) {
	if (this.byLetter) {
	    if (!this.text) {
		this.text = this.curElt.firstChild.data;
		this.textIndex = 1;
		this.curElt.style.visibility = 'visible';
		this.curElt.appendChild(this.cursor);
	    }

	    if (this.textIndex <= this.text.length) {
		this.curElt.firstChild.data =
		    this.text.substring(0, this.textIndex);
		this.textIndex++;
		setTimeout(this.show.bind(this, next), this.speed);
	    } else {
		this.text = undefined;
		setTimeout(this.prepare.bind(this, next), this.pauseAfter);
	    }
	} else {
	    this.curElt.style.visibility = 'visible';	
	    this.curElt.appendChild(this.cursor);
	    setTimeout(this.prepare.bind(this, next), this.pauseAfter);
	}
    },

    blink : function() {
	if (this.cursor.style.visibility == 'visible')
	    this.cursor.style.visibility = 'hidden';
	else
	    this.cursor.style.visibility = 'visible';
	setTimeout(this.blink.bind(this), this.cursorBlink);
    },

    start : function(ids, next) {
	this.curIndex = -1;
        if (ids)
	    this.getByIds(ids);
	else
	    this.getElts();
	this.prepare(next);

        if (!this.cursor) {
	    this.cursor = document.createElement('span');
	    this.cursor.appendChild(document.createTextNode('_'));
	    this.blink();
	}
    }
}
