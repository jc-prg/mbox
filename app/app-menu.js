//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// class for drop down menu
//--------------------------------------
/* INDEX:
function jcMenu(name, menu, title)
        this.init = function(data=[])
        this.empty = function(data=[])
	this.add_script = function(script,label)
	this.add_line = function()
	this.add_link = function(link,label)
	this.entry_link   = function (link,label)
	this.entry_script = function (script,label)
	this.set_title = function(title)
        this.log = function(msg)
*/
//--------------------------------------

function jcMenu(name, menu, title) {

	this.menuItems = menu;
	this.menuTitle = title;
        this.app_name  = name;
	this.data      = {};


        // load data with devices (deviceConfig["devices"])
        this.init = function(data=[]) {
                this.data = data;
                this.log("Initialized new class 'jcMenu'.");
    		setTextById(this.menuItems,"");
                }

        // load data with devices (deviceConfig["devices"])
        this.empty = function(data=[]) {
    		setTextById(this.menuItems,"");
                }


	// add links to scenes to drop down menu
	this.add_script = function(script,label) {

		// set vars
    		var menu = getTextById(this.menuItems);

		// create link for javascript
		menu += this.entry_script(script,label);

		// replace old menu
    		setTextById(this.menuItems,menu);
		}


	// add links to scenes to drop down menu
	this.add_line = function() {
		// set vars
    		var menu = getTextById(this.menuItems);

		// create link for javascript
		menu += "<hr width=\"90%\" height=\"1px\" />";

		// replace old menu
    		setTextById(this.menuItems,menu);
		}

	// add links to scenes to drop down menu
	this.add_link = function(link,label) {

		// set vars
    		var menu = getTextById(this.menuItems);

		// create link for javascript
		menu += this.entry_link(link,label);

		// replace old menu
    		setTextById(this.menuItems,menu);
		}

	// menu entries
	this.entry_link   = function (link,label) {
   		return "<li><a href=\"" + link + "\" target=\"_blank\">" + label + "</a></li>";
		}

	this.entry_script = function (script,label) {
  		return "<li><a onClick=\"javascript:" + script + ";clickMenu();setNavTitle('" + label + "');\">"+label+"</a></li>";
		}

	this.set_title = function(title) {
		title = "<div onClick=\"javascript:if(mbox_settings){settingsToggle();};appCookie.erase('appCookie');\">"+title+"</div>";
		setTextById(this.menuTitle,title);
		}

        // handle messages for console
        this.log = function(msg) {
                console.log(this.app_name + ": " + msg);
                }
	}


//------------------------------------------
// EOF

