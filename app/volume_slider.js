//-----------------------------------------
// slider for volume control
//-----------------------------------------
/* INDEX
function slider ( name, container, callOnChange )
	this.init    = function( min, max, label )
		this.slider.oninput = function( )
		this.slider.onmousedown = function()
		this.slider.onmouseup = function()
		this.slider.ontouchstart = function()
		this.slider.ontouchend = function()
	this.set_value = function( value )
	this.show_hide = function()
*/
//-----------------------------------------

var main_audio = "test";

function slider ( name, container ) {

	this.appName      = name;
	this.appContainer = container;
	this.callOnChange = this.info;
	this.showVolume   = this.info;
	
	// set callback functions
	this.setOnChange	= function(callOnChange) {
		if (callOnChange != "") { this.callOnChange = callOnChange; }
		else			{ this.callOnChange = this.info; }
		}
		
	this.setShowVolume	= function(showVolume,showVolumeContainer) {
		if (showVolume != "")	{ this.showVolume = showVolume; this.showVolumeContainer = showVolumeContainer; }
		else			{ this.showVolume = this.info;  this.showVolumeContainer = ""; }
		}
		
	// initialize slider
	this.init	= function( min, max, label ) {
		name = this.appName;

		if (this.container == undefined) {
			this.sliderHTML   		=  "<div id=\""+name+"_container\" class=\"slidecontainer\" style=\"visibility:hidden\">";
  			this.sliderHTML   		+= "<input type=\"range\" min=\""+min+"\" max=\""+max+"\" value=\"50\" class=\"slider\" id=\""+name+"\">";
  			this.sliderHTML   		+= "<br/><div id=\""+name+"_value\" class=\"slidervalue\">xx</div>";
  			this.sliderHTML   		+= "<div  id=\""+name+"_label\" class=\"sliderlabel\">"+label+"</div>";
			this.sliderHTML   		+= "</div>";
	
			this.container    		= document.getElementById(this.appContainer);
			this.container.innerHTML	= this.sliderHTML;

			this.slider       		= document.getElementById(name);
			this.slider_value 		= document.getElementById(name+"_value");
			this.slider_cont  		= document.getElementById(name+"_container");
			this.slider_label 		= document.getElementById(name+"_label");
			this.slider_active		= false;
			}

		this.slider_value.innerHTML	= this.slider.value;
		this.slider_label.innerHTML	= "Device: " + label;
	
		this.appMainAudio 		= main_audio;
		this.appMainAudioLabel		= label;
		this.audioMin     		= min;
		this.audioMax     		= max;
		
		this.slider.oninput	= function( ) {
			mboxSlider.slider_value.innerHTML	= mboxSlider.slider.value;
			console.log("Set Volume: " + mboxSlider.slider.value);  
			//this.slider_value.innerHTML 		= this.slider.value;

			vol_color = "white";
			vol_str   = this.showVolume( mboxSlider.slider.value, mboxSlider.audioMax, vol_color );
			document.getElementById( mboxSlider.showVolumeContainer ).innerHTML = vol_str;
			}
		
		this.slider.onmousedown	= function() { mboxSlider.slider_active = true; }
		this.slider.onmouseup	= function() {
			//this.callOnChange( this.slider.value );
			mboxSlider.callOnChange( mboxSlider.appMainAudio, mboxSlider.slider.value );
			mboxSlider.slider_active = false;
			}

		this.slider.ontouchstart= function() {	mboxSslider.slider_active = true;	}
		this.slider.ontouchend	= function() {
			//this.callOnChange( this.slider.value );
			mboxSlider.callOnChange( mboxSslider.appMainAudio, mboxSslider.slider.value );
			mboxSlider.slider_active = false;
			}
		}
				
	// set value from outside (update data)
	this.set_value	= function( value ) {
		if (this.slider_active == false) {
			this.slider.value		= value;
			this.slider_value.innerHTML	= value;
			}
		console.log("Set Volume: " + this.slider.value);  
		}
		
	// show or hide slider
	this.show_hide	= function() {
		if (this.slider_cont.style.visibility == "hidden") 	{ this.slider_cont.style.visibility = "visible"; }
		else							{ this.slider_cont.style.visibility = "hidden"; }
		}
	
	this.info	= function() {
		alert("Please define a function to be called on change.");
		}
		
	}

//-----------------------------------------
// EOF
