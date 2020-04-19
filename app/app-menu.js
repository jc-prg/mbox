//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// class for drop down menu
//--------------------------------------
/* INDEX:
function appMenuDefinition(name, menu, title)
        this.init 		= function(data=[])
        this.empty 		= function()
	this.add_script 	= function(script,label)
	this.add_line 		= function()
	this.add_link 		= function(link,label)
	this.entry_link		= function (link,label)
	this.entry_script 	= function (script,label)
	this.set_title 		= function(title)
        this.log 		= function(msg)
        this.writeMenu		= function(menutext)
        this.readMenu		= function()
*/
//--------------------------------------

function appMenuDefinition(name, menu, title) {

	this.menuItems   = menu;
	this.menuTitle   = title;
        this.app_name    = name;
        this.inital_load = true;
	this.data        = {};


        // load data with devices (deviceConfig["devices"])
        this.init 		= function(data=[]) {
        	if (data["DATA"]) 	{ this.data = data; }
        	else			{ return; }
                
                if (this.initial_load) { 
                	this.log("Initialized new class 'jcMenu'.");
                	this.inital_load = false;
                	}
                else {
                	this.log("Reload data 'jcMenu'.");
                	}

    		this.empty();

    		// define variable menu size (scroll bars defined in app-menu.css)
    		window.onresize = function(event) {
    			height = (window.innerHeight - 70);
    			document.getElementById("menuItems").style.maxHeight  = height + "px"; 
    			document.getElementById("menuItems2").style.maxHeight = height + "px"; 
    			appMenu.menu_height();	
			}

		height = (window.innerHeight - 70);
		document.getElementById("menuItems").style.maxHeight   = height + "px"; 
		document.getElementById("menuItems2").style.maxHeight  = height + "px";
		this.menu_height();	
                }

        this.menu_height	  = function() {
   		document.getElementById("remote_nav").style.maxHeight = "100px"; // window.innerHeight + "px"; // 
	        var height = pageHeight();
	        height    -= 50;
   		document.getElementById("remote_nav").style.maxHeight = height+ "px"; // window.innerHeight + "px"; // 
   		console.error(height);
        	}

        // load data with devices (deviceConfig["devices"])
        this.empty 		= function() {
    		this.writeMenu("");
                }


	// add links to scenes to drop down menu
	this.add_script 	= function(script,label) {

    		var menu = this.readMenu();
		menu += this.entry_script(script,label);
    		this.writeMenu(menu);
		}


	// add links to scenes to drop down menu
	this.add_line 		= function() {
	
    		var menu = this.readMenu();
		menu += "<hr width=\"90%\" height=\"1px\" />";
    		this.writeMenu(menu);
		}

	// add links to scenes to drop down menu
	this.add_link 		= function(link,label) {

    		var menu = this.readMenu();
		menu += menuEntry(link,label);
    		this.writeMenu(menu);;
		}

	// menu entries
	this.entry_link		= function (link,label) {
   		return "<li><a href=\"" + link + "\" target=\"_blank\">" + label + "</a></li>";
		}

	this.entry_script 	= function (script,label) {
  		return "<li><a onClick=\"javascript:" + script + ";clickMenu();mboxHtmlSetNavTitle('" + label + "');\">"+label+"</a></li>";
		}

	this.set_title 		= function(title) {
		title = "<div onClick=\"javascript:if(mbox_settings){mboxSettingsToggle();};appCookie.erase('appCookie');\">"+title+"</div>";
		setTextById(this.menuTitle,title);
		}

        // handle messages for console
        this.log 		= function(msg) {
                console.log(this.app_name + ": " + msg);
                }
                
        // write data to menu
        this.writeMenu		= function(menutext) {
        	if (typeof this.menuItems == "string") {
        		setTextById(this.menuItems,menutext);
        		}
        	else if (typeof this.menuItems == "object") {
        		for (var i=0; i<this.menuItems.length; i++) {
	        		setTextById(this.menuItems[i],menutext);
        			}
        		}
        	}
        	
        // read data from menu
        this.readMenu		= function() {
        	if (typeof this.menuItems == "string") {
        		return getTextById(this.menuItems);
        		}
        	else if (typeof this.menuItems == "object") {
        		return getTextById(this.menuItems[0]);
        		}
        	}
	}


//------------------------------------------
// EOF

