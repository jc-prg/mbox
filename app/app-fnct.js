//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// several functions ...
//--------------------------------------
/* INDEX:
function showReturnMsg(data) {
function pausecomp(ms) {
function pausecmd(s) {
function convert_second2time(seconds) {
function setTextById(id, text="") {
function addTextById(id, text="") {
function getTextById(id, text="") {
function setOnclickById(id, script="") {
function isHidden(id) {
function elementHidden(id) {
function elementVisible(id) {
function changeVisibility(id) {
function writeKeyBoard () {
function sortNumber(a,b) {
*/
//--------------------------------------

// Warten
//--------------------------------

function pausecomp(ms) {
    ms += new Date().getTime();
    while (new Date() < ms){}
    }

function pausecmd(s) {
    s = s*1000;
    s += new Date().getTime();
    while (new Date() < s){
		}
    }

//--------------------------------

function convert_second2time(seconds) {
	var min = Math.floor(seconds/60);
	var sec = seconds - min*60;
	if (sec < 10) { sec = "0"+sec; }
	return (min+":"+sec);
	}


//--------------------------------
// set & get text to element
//--------------------------------

function setTextById(id, text="") {
	if (document.getElementById(id)) {
		document.getElementById(id).innerHTML = text;
		}
	else { console.error("setTextById: ERROR Element not found - "+id); }
	}

function addTextById(id, text="") {
	if (document.getElementById(id)) {
		document.getElementById(id).innerHTML += text;
		}
	else { console.error("setTextById: ERROR Element not found - "+id); }
	}

function getTextById(id, text="") {
	if (document.getElementById(id)) {
 		return document.getElementById(id).innerHTML;
  		}
	else { return false; } // it's OK, when not found - as used to check
	}

function setOnclickById(id, script="") {
	if (document.getElementById(id)) {
		document.getElementById(id).onclick = function() { eval(script); };
		if (script == "") 	{ document.getElementById(id).style.cursor = "default"; }
		else			{ document.getElementById(id).style.cursor = "pointer"; }
		}
	else { console.error("setOnClickById: ERROR Element not found - "+id); }
	}

//--------------------------------
// check if element is hidden
//--------------------------------

function isHidden(id) {
  var element = document.getElementById( id );
  var style   = window.getComputedStyle( element );
  return (style.display == 'none');
  }

//--------------------------------
// change visibility of element
//--------------------------------

function elementHidden(id) {
	if (document.getElementById(id)) {
	  	document.getElementById(id).style.display = "none";
		}
  	}

function elementVisible(id) {
	if (document.getElementById(id)) {
	  	document.getElementById(id).style.display = "block";
		}
  	}

function changeVisibility(id) {
	if (document.getElementById(id)) {
		if (document.getElementById(id).style.display != "block")  	{ elementVisible(id); }
  		else               						{ elementHidden(id); }
		}
	else { console.error("changeVisibility: ERROR Element not found - "+id); }
  	}

//--------------------------------------

function writeKeyBoard () {
   var test = "<ul>";
   for (var i=8500;i<15000;i++) {
       test = test + "<li>" + i + " &nbsp; [ &#"+i+"; ]</li>";
       }
   test = test + "</ul>";
   return test;
   }

//--------------------------------------

function sortNumber(a,b) {
        return a - b;
    }

