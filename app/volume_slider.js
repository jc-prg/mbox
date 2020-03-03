//-----------------------------------------
// slider for volume control
//-----------------------------------------
/* INDEX
function slider ( name, container, callOnChange )
*/
//-----------------------------------------

function slider ( name, container, callOnChange ) {

	this.appName      = name;
	this.appContainer = container;
	this.callOnChange = callOnChange;

	// initialize slider
	this.init    = function( min, max, label ) {
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
		this.slider_label.innerHTML	= label + " (" + main_audio + ")";
	
		this.appMainAudio 		= main_audio;
		this.appMainAudioLabel		= label;
		this.audioMin     		= min;
		this.audioMax     		= max;
		
		this.slider.oninput = function( ) {
			rm3slider.slider_value.innerHTML	= rm3slider.slider.value;
			console.log("Set Volume: " + rm3slider.slider.value);  
			//this.slider_value.innerHTML 		= this.slider.value;

			vol_color = "white";
			vol_str   = show_volume( rm3slider.slider.value, rm3slider.audioMax, vol_color );
			document.getElementById("audio3").innerHTML = vol_str;
			}
		
		this.slider.onmousedown = function() { rm3slider.slider_active = true; }
		this.slider.onmouseup = function() {
			//this.callOnChange( this.slider.value );
			rm3slider.callOnChange( rm3slider.appMainAudio, rm3slider.slider.value );
			rm3slider.slider_active = false;
			}

		this.slider.ontouchstart = function() {	rm3slider.slider_active = true;	}
		this.slider.ontouchend = function() {
			//this.callOnChange( this.slider.value );
			rm3slider.callOnChange( rm3slider.appMainAudio, rm3slider.slider.value );
			rm3slider.slider_active = false;
			}
		}
				
	// set value from outside (update data)
	this.set_value = function( value ) {
		if (this.slider_active == false) {
			this.slider.value		= value;
			this.slider_value.innerHTML	= value;
			}
		console.log("Set Volume: " + this.slider.value);  
		}
		
	// show or hide slider
	this.show_hide = function() {
		if (this.slider_cont.style.visibility == "hidden") 	{ this.slider_cont.style.visibility = "visible"; }
		else							{ this.slider_cont.style.visibility = "hidden"; }
		}
		
	}

//-----------------------------------------
// EOF



























