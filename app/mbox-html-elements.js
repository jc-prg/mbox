//--------------------------------------
// jc://music-box/, (c) Christoph Kloth
//--------------------------------------
// INDEX:
// ------
// function show_data_object(data) {}
// function add_link(link, description="") {}
// function button (onclick,label, id="") {}
// ------
// function mboxTable(p1,p2="",p3="",p4="") {}
// function mboxScrollTo(type, uuid="") {}
// function mboxAlbumDetail( count ) {}
// function mboxToolTip( type, count=0, input_text="" ) {}
// function mboxButton( button, cmd="", color="blue", small="", display="block" ) {}
// function mboxCoverList( uuid, cover="", cmd_open="", cmd_play="" ) {}
// function mboxCoverSeparator( content, cmd ) {}


//-------------------------------------------------------------

function mboxCoverSeparator( content, cmd ) {

	var text = "";
        text += "<div class=\"album_cover\" style=\"background:#eeeeee;background-size:cover;background-position:center;background-repeat:no-repeat;\" onclick='" + cmd + "'>";
        text += "<div class=\"album_plus\">" + content + "</div>";
        text += "</div>";
	return text;
	}


//-------------------------------------------------------------

function mboxCoverList( uuid, cover="", description="", cmd_open="", cmd_play="", type="album" ) {

	var text          = "";
	var button_play   = "";
	var default_cover = mbox_icons[type];
	var icon_playing  = mbox_icons["playing"];

        if (mbox_device == "remote") {
		button_play = "<div class=\"player_button small white\" onclick=\"" + cmd_play + "\"><img src=\"icon/play.png\" style=\"width:9px;height:9px;margin:2px;\"></div>";
		}

	if (cover == "") {
                cover = default_cover;
                text += "<div class=\"album_cover\" style=\"background:url(" + cover + ");\" onclick=\"" + cmd_open + "\">";
		text += button_play;
                text += "<div class=\"player_active\" id=\"playing2_" + uuid + "\" style=\"display:none;\"><img src=\"" + icon_playing + "\" style=\"width:10px;height:10px;margin:2px;\"></div>";
                text += "<br/><br/>";
                text += description + "<br/>";
                text += "</div>";
                }
        else {
                text += "<div class=\"album_cover\" style=\"background:url(" + cover + ");background-size:cover;background-repeat:no-repeat;vertical-align:botton;\" onclick=\"" + cmd_open + "\">";
		text += button_play;
                text += "<div class=\"player_active\" id=\"playing2_" + uuid + "\" style=\"display:none;\"><img src=\"" + icon_playing + "\" style=\"width:10px;height:10px;margin:2px;\"></div>";
                text += "</div>";
                }

	return text;
	}


//-------------------------------------------------------------

function mboxButton( button, cmd="", color="blue", small="", display="block" ) {

        var text  = "";

        if (button != "empty") {
                text +=   "<div class=\"player_button "+color+" "+small+"\" onclick=\"javascript:"+cmd+"\" style=\"display:"+display+";\">";
                text +=   "<img src=\"icon/"+button+".png\" class=\"player_image "+small+"\"></div>";
                }
        else {
                text +=   "<div class=\"player_button empty "+small+"\"></div>";
                }

        return text;
        }

//-------------------------------------------------------------

function mboxToolTip( type, count=0, input_text="" ) {

	var text = "";
	if (type == "start") {
	        text += "<div class='tooltip'>";
		}
	else if (type == "end") {
	        text += "<span class='triangle1'></span>";
        	text += "<span class='triangle2'></span>";
	        text += "<span class=\"tooltiptext " + mboxTooltipLeft(count) + "\">" + input_text + "</span>";
        	text += "<div class='album_triangle'  id=\"album_tri1_" + count + "\"></div>";
	        text += "<div class='album_triangle2' id=\"album_tri2_" + count + "\"></div>";
        	text += "</div>";
		}
	return text;
	}

//-------------------------------------------------------------

function mboxScrollTo( type, uuid="" ) {
	var text = "";
	if (type == "start") {
		text += "<div id=\"scrollto_" + uuid.replace(/-/g,"") + "\">";
		}
	else if (type == "end") {
		text += "</div>";
		}
	return text;
	}

//-------------------------------------------------------------

function mboxAlbumDetail( count ) {
	var text = "";
	text += "<div class=\"album_detail\" id=\"album_"+count+"\" style=\"display:none\">"+count+" / " + document.body.clientWidth + "</div>";
	return text;
	}


//-------------------------------------------------------------

function show_data_object(data) {
	if (data) {
	        var str = JSON.stringify(data);
        	str = str.replace(/,/g,",<br/>");
        	str = str.replace(/{/g,"{<br/>");
        	str = str.replace(/}/g,"}<br/>");
		}
	else {
		str = "Not data returned!";
		}

        appMsg.confirm(
       	        "<div style=\"text-align:left;overflow:auto;width:95%;height:200px;border:solid 1px;\">"+str+"</div>",
               	"",280);
        }


//-------------------------------------------------------------

function mboxTableNew( cells=[], divide=false, width="100%", height="" ) {

        // set width of colums
	if (divide) 	{ var cell_width = 100 / cells.length + "%"; }
	else		{ var cell_width = ""; }

        // return start, end or row
        if (cells == "start")      { return "<table border=\"0\" width=\"" + width + "\" height=\"" + height + "\">"; }
        else if (cells == "end")   { return "</table>"; }
	else  {
		var text = "<tr>";
		for (var i=0;i<cells.length;i++) { text += "<td width=\"" + cell_width + "\">" + cells[i] + "</td>"; }
		text    += "</tr>";
		return text;
		}
        }


//-------------------------------------------------------------

function mboxTable(p1,p2="",p3="",p4="") {

        // set width of colums
        var w = [];
        if (p2=="" && p2 != 0 && p3=="" && p4=="")      { w = ["100%","0%","0%","0%"]; }
        else if (p3=="" && p4=="")       	      	{ w = ["50%","50%","0%","0%"]; }
        else if (p4=="")                 	 	{ w = ["33%","33%","33%","0%"]; }
        else                                    	{ w = ["25%","25%","25%","25%"]; }

        // return start, end or row
        if (p1 == "start")      { return "<table border=\"0\" width=\"100%\">"; }
        else if (p1 == "end")   { return "</table>"; }
	else                    { return "<tr><td width=\""+w[0]+"\">"+p1+"</td><td width=\""+w[1]+"\">"+p2+"</td><td width=\""+w[2]+"\">"+p3+"</td><td width=\""+w[3]+"\">"+p4+"</td></tr>"; }
        }


//-------------------------------------------------------------

function input_element( name, data ) {
	var text = "";

	if (typeof data == "string") { text += "<input id='"+name+"' name='"+name+"' value='"+data+"'>"; }
	else if (data) {
	        var str = JSON.stringify(data);
        	str = str.replace(/,/g,",<br/>");
        	str = str.replace(/{/g,"{<br/>");
        	str = str.replace(/}/g,"}<br/>");
		text += "<div id='"+name+"' style='border:solid 1px lightgray;background:#eeeee;width:250px;height:60px;overflow:auto;'>"+str+"</div>";
		}

	return text;
	}

//-------------------------------------------------------------

function button (onclick,label, id="") {
        return "<button style=\"width:150px;margin:1px;\" onClick=\"javascript:"+onclick+"\" id=\""+id+"\">"+label+"</button>";
        }


//-------------------------------------------------------------

function add_link(link, description="") {
        if (description == "") { description = link; }
        return "<a href=\"" + link + "\" target=\"_blank\" style=\"color:white\">" + description + "</a><br/>";
        }


