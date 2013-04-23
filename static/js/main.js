// ------------------------------------------------------------------------------ //
// PROGRAM CONTROL
var MODE;				// active mode
var _MODE; 				// inactive mode
var EXAMPLE_STATE;		// example under <input> open or not
var EXAMPLE_SENT = 'off'// example sentence show or not

var QUERY_URL; 			// encoded query

// BROWSER CONTROL
var BROWSER;
var VERSION;
// var CHROME  = false;
// var SAFARI  = false;
// var FIREFOX = false;
// var IE      = false;
var SPEECH_SUPPORT = false;

// AJAX CONTROL
var QUERY_SERVICE_TIMEOUT = 90000;
var SENT_SERVICE_TIMEOUT = 10000;

// UI CONTROL
var RESULT_COL = 0; 	// # of cols in a result block
var BAR_ANIMATE = 1000;
// ------------------------------------------------------------------------------ //
$(document).ready(function(){
	// console.log("XD");
	EXAMPLE_STATE = 'on';
	layout();
	events();
	init();
	// _test_cluster();
});
// ------------------------------------------------------------------------------ //

function init() // a page load (ajax)
{
	var B = detectBrowswer();

	BROWSER = B.browser;
	VERSION = B.version;

	// B.IEVERSION
	adjustBrowser();

	infofetch(); 					// detect the query
	setMode();						// set query mode
	$("body").click();				// close the help field

	layout();						// set layout
	exampleHandler(EXAMPLE_STATE);	// example show/hide

	// console.log(test());
}
function adjustBrowser()
{
	// alert(BROWSER);
	// $.each($.browser, function(x){
		// alert(x);
	// });
	// alert(BROWSER);
	$("#search-bar").addClass("search-bar-"+BROWSER);
}
// ------------------------------------------------------------------------------ //

// function detectBrowswer()
// {
	// browsers = {"chrome":}

	// if($.browser.chrome)CHROME = true;
	// else if ($.browser.safari)SAFARI = true;

	// if(CHROME) SPEECH_SUPPORT = true;
// }

function detectPlatform()
{
	if(navigator.platform.indexOf('iPad'))
	{

	}else if(navigator.platform.indexOf('MacIntel'))
	{

	}
	
	
}

function redirect(query, mode)
{
	window.location = '#' + query + '#' + mode;
}
function inputEmpty()
{
	// the query in search field is empty
	if($.trim($("#search-bar").val()).length == 0){
		EXAMPLE_STATE = 'on';
		exampleHandler(EXAMPLE_STATE);
	}
}
function events()
{
	/// AJAX LOAD PAGE
	$(window).hashchange(function(){ init(); });

	/// LAYOUT EVENT
	$(window).resize(function(){ layout(); });


	/// SEARCH EVENT
	// ! Modify the search event here !
	$("#search-button").click(function(){
		EXAMPLE_STATE = 'off';
		exampleHandler(EXAMPLE_STATE);
		// set url, this will trigger the $(window).hashchange event and perform the search
		var query = encodeURIComponent($.trim($("#search-bar").val()));
		// window.location = '#' + query;
		redirect(query, MODE);
	});
	/// SEARCHBAR EVENT
	$("#search-bar").keyup(function(e){
		// control "Enter"
		if(e.keyCode == 13 || e.which == 13) {

			$("#search-button").click(); // trigger search event
		}
		// control "Up" & "Down" while the example field is expanded
		else if(e.keyCode == 40 || e.keyCode ==38) {
			if(EXAMPLE_STATE == 'on') { // if example on
				updown(e.keyCode);
			}
		}
		else if (e.keyCode == 8)
		{
			EXAMPLE_STATE = 'on';
			exampleHandler(EXAMPLE_STATE);
		}
		else{
			// input any character, close example
			EXAMPLE_STATE = 'off';
			exampleHandler(EXAMPLE_STATE);
		}
		inputEmpty();

	}).hover(function(){
		$("#search-bar-container").toggleClass("bar-hover");
	}).focus(function(){
		$("#search-bar-container").removeClass("bar-normal").addClass(MODE+"-bar-focus");
	}).blur(function(){
		$("#search-bar-container").removeClass(MODE+"-bar-focus").addClass("bar-normal");
	}).change(function(){
		inputEmpty();
	}).click(function(){
		inputEmpty();
	});


	/// EXAMPLE EVENT
	$("#search-example").click(function(){
		// toggle example
		if(EXAMPLE_STATE == 'on') EXAMPLE_STATE = 'off';
		else EXAMPLE_STATE = 'on';

		exampleHandler(EXAMPLE_STATE);
	});
	$(".option-container").live('click touchstart',function(){
		choose(parseInt($(this).attr("idx")));		// highlight the selected item


		var query = $(this).find(".option").html().split("<span>")[0];

		if(BROWSER == 'msie' && VERSION == '8.0')
		{
			query = $(this).find(".option").html().match(/([^<]+)/gi)[0];
		}


		// var query = $(this).find(".option").text();	// send query to search bar
		$("#search-bar").val(query);
		$("#search-example").click();				// close the example field
		$("#search-button").click();				// perform search
	}).live("hover",function(){
		$(this).toggleClass(MODE+"-hover");
	});

	/// HELP EVENT
	$("#search-help").click(function(e){
		e.stopPropagation(); 						// prevent from triggering body event as below
		$("#help-container").show(0);				// show help
		$("#help-mask").show(0,function(){			// show help mask
			$("body").css("overflow","hidden"); 	// disable the scroll bar
		});

	});
	$("body").bind('click touchstart', function(){ 					// press anywhere to close the help
		$("#help-container").fadeOut(0, function(){
			$("#help-mask").hide(0,function(){
				$("body").css("overflow","auto");	// restore the scroll bar
			});
		});
	});
	$("#help-container").click(function(e){
		e.stopPropagation(); 						// if click the help, do nothing
	});

	// MODE CHANGE EVENT
	$("#HLI-img").click(function(){
		redirect("", "HLI");
	});
	$("#CMD-img").click(function(){
		redirect("", "CMD");
	});


	// EXAMPLE SENTENCE EVENT
	$(".expand-example").live('click',function(e){

		var ngramText = $(this).parents(".ngram").find(".phrase-container").find(".text").text();
		var anchor = $(this);
		$.ajax({
		    url: "examples/" + ngramText,
		    dataType: "json",
		    // data:"ngram="+ngramText,
		    type: "GET",
		    timeout: SENT_SERVICE_TIMEOUT, // reset timeout!!!!
		    success: function(exampleSents) {
		    	// console.log(exampleSents);
		    	var exSents = exampleSents.Examples;

		    	fillExampleSents(exSents, anchor, ngramText);


		    	// alert(ngram)

		    },
		    complete: function(data) {},
		    error: function(x, t, m) { if(t==="timeout") {/*console.log("got timeout");*/} else {/*console.log(t);*/} }
		});
		e.stopPropagation(); // prevent trigger parent event, or may cause loop trigger
	});
	$(".note-container").live("click",function(){
		// if(EXAMPLE_SENT == 'on'){
			// alert("XD");
			$(this).parent().find(".expand-example").click();
		// }
	});
	$(".ngram").live("click",function(){
		$(this).find(".expand-example").click();
	});

	// more event
	$('.more-text').live('click',function(e){
		$(this).parents('.cluster').find('.fold-target').toggleClass('hide');
		$(this).parent().find('.more-text').toggleClass('hide');
	});		
}
function fillExampleSents(sents, anchor, ngramText)
{

	var tr = anchor.parents(".ngram");
	var idx = tr.attr("index");

	tr.toggleClass("expand");

	if(tr.hasClass("expand"))
	{
		ref = tr;
		// expand example
		$.each(sents, function(i){
			if($.trim(sents[i]).length > 0 )
			{
				var sent = $("<tr/>").attr("index",idx).addClass("block example-sent").insertAfter(ref);
				// add note img
				var note = $("<td/>").addClass("note-container").appendTo(sent);
				// $("<img/>").addClass("note-img").attr("src","media/data/arrow.png").appendTo(note);
				// add sent
				var sentContainer = $("<td/>").addClass("ex-sent-container").attr("colspan", RESULT_COL-1).appendTo(sent);
				var markupSent = sents[i].replace(ngramText, "<b>"+ngramText+"</b>");
				$("<div/>").addClass("ex-sent").html(markupSent).appendTo(sentContainer);
				ref = sent;
			}
		});

		// check the empty example sentences
		var sentNum = $('.example-sent[index="'+idx+'"]').length;
		if(sentNum == 0)
		{
			// remove expand option and ditatch event
			anchor.find(".plus-btn").remove();
			anchor.find(".minus-btn").remove();
			tr.removeClass("expand");

		}else{
			// change to minus icon
			anchor.find(".plus-btn").hide(0);
			anchor.find(".minus-btn").show(0);
		}
	}else
	{
		// shrink example
		$('.example-sent[index="'+idx+'"]').remove();

		// change to plus icon
		anchor.find(".plus-btn").show(0);
		anchor.find(".minus-btn").hide(0);
	}
}
function exampleHandler(on_off)
{
	if(on_off.toLowerCase() == 'off')
	{
		$(".option-container").addClass("hide");	// close the examples
	}else
	{
		$(".option-container").removeClass("hide");	// open the examples
	}
	$("#search-bar").focus();						// focus on the search bar
	layout();
	EXAMPLE_STATE = on_off;
}
// control the up-down arrow key
function updown(k)
{

	var selected = $(".selected");
	var last = $(".option-container").length-1;
	var idx = selected.attr("idx");

	if(!idx)
	{
		idx = -1;
	}else
	{
		idx = parseInt(idx);
	}
	if(k == 40)
	{
		// down
		shift = 1;
		if(idx == last)shift = 0;

	}else if(k == 38)
	{
		// up
		shift = -1;
		if(idx == 0)shift = 0;
	}
	choose(idx + shift);
}
// select example acoording to idx
function choose(idx)
{
	var _target = $(".option-container").eq(idx);
	$(".option-container").removeClass("selected");
	_target.addClass("selected");
	var query = _target.find(".option").html().split("<span>")[0];
	$("#search-bar").val(query);
}
function getExampleSent(ngram)
{
	$.ajax({
	    url: "examples/",
	    dataType: "json",
	    data:"ngram="+ngram,
	    type: "GET",
	    timeout: SENT_SERVICE_TIMEOUT, // reset timeout!!!!
	    success: function(exampleSents) {
	    	alert(exampleSents);
	    	// getPatternResult(server, query);

	    },
	    complete: function(data) {},
	    error: function(x, t, m) { if(t==="timeout") {/*console.log("got timeout");*/} else {/*console.log(t);*/} }
	});
}
function showMsg(msg)
{
	var tr = $("<tr/>").addClass("block").appendTo($("#result-block"));
	var td = $("<td/>").addClass("no-result").appendTo(tr);
	$("<span/>").text(msg).appendTo(td);
}

function _clear_previous_results()
{
	$('#cluster-tag-container').html('');
	$('#clusters-container').html('');
	$('#result-block').html('');


}
function getPatternResult(server, query)
{
	// alert(query);
	$.ajax({
	    url: server + query,
	    // url: "static/go_home.json",
	    // url: "static/cultivate_N.json",
	    type: "GET",
	    dataType: "json",
	    timeout: QUERY_SERVICE_TIMEOUT, // 15 sec
	    success: function(recv) {

			var mode = recv[0];
			var data = recv[1];	    	

			_clear_previous_results()

			if(mode == 'new')
			{
				_extract_cluster(data);
				$('#result-block').addClass('hide');
				$('#result-block-container').removeClass('hide');
				
			}
			else if(mode == 'old')
			{
				// console.log(data);
				showResult(data);
				$('#result-block-container').addClass('hide');
				$('#result-block').removeClass('hide');				
			}			
/////// 
/////// IMPLEMENT THE NEW QUERY HERE
/////// ..........
/////// ..........
///////

			 	// show data
			layout(); 			// adjust layout
			fill(BAR_ANIMATE); 		// animate
	    },
	    complete: function(data) {

			// no matter success or error, close loading img
			$("#search-loading").find("img").hide(0);

			// console.log(data.responseText);

			if(data.responseText.length <= 2)
			{

				// show no result
				showMsg("no result.");

				// show try HLI or try CMD
				if(MODE == "CMD") var text = "Try Human Input";
				else var text = "Try Command Mode";

				$("<span/>").text(text).attr('id','try-'+_MODE).appendTo(td).click(function(){
					redirect(query,_MODE);
				});

			}else{
				// show command convert result
		    	if(MODE == "HLI") {
					$('#cmd-convert-result').text("Command:");
					$("<span/>").text(query).appendTo($('#cmd-convert-result')).click(function(){
						redirect(encodeURIComponent(query),"CMD");
					});
				}
			}
	    },
	    error: function(x, t, m) {
	        if(t==="timeout") {
				showMsg("got timeout...");
	            // console.log("got timeout");
	        } else {
	        	showMsg("internal server error. :(");
	            // console.log(t);
	        }
	    }
	});
}
function query()
{
	var server = "query/";
	var query;

	// clear current result
	$("#result-block").html("");

	// loading img show
	$("#search-loading").find("img").show(0);

	var searchBarValue = $.trim($("#search-bar").val());
	encode_query = encodeURIComponent(searchBarValue);

	if(MODE == 'CMD')
	{
		getPatternResult(server, encode_query);

	}else if(MODE == 'HLI')
	{
		$.ajax({
		    url: "sent/"+encode_query,
		    type: "GET",
		    timeout: SENT_SERVICE_TIMEOUT,
		    success: function(query) {
		    	getPatternResult(server, query);

		    },
		    complete: function(data) {},
		    error: function(x, t, m) { if(t==="timeout") {/*console.log("got timeout");*/} else {/*console.log(t);*/} }
		});
	}


}
function showResult(data)
{
	// clear current result
	$("#result-block").html("");

	// <table #result-block>
	// 	<tr .block>
	// 		<td .note-container>
	// 		<td .phrase-container>
	// 		<td .count-container>
	// 		<td .percent-container>
	//		<td .expand-example>


	if(data.length > 0)
	{
		// extract the data
		$.each(data, function(i){

			// extract results
			var block = $("<tr/>").attr("index",i).addClass("block ngram").appendTo($("#result-block"));

			// note container
			// var note = $("<td/>").addClass("note-container").appendTo(block);
			// $("<img/>").addClass("note-img").attr("src","static/img/note.png").appendTo(note);

			// pharse container
			var phraseContainer = $("<td/>").addClass("phrase-container").appendTo(block);
			$("<div/>").addClass("text").html(data[i].phrase).appendTo(phraseContainer);
			// alert(restore(data[i].percent));

			// phraseWidth = parseInt($('.phrase-container').css('width'))
			// console.log('phraseWidth:',phraseWidth)
			// console.log('percent:',restore(data[i].percent))
			// console.log('bar:',restore(data[i].percent)*phraseWidth)
			var bar = $("<div/>").addClass("bar").attr("length", restore(data[i].percent)*580).appendTo(phraseContainer);

			// count container
			var countContainer = $("<td/>").addClass("count-container").attr("total",data[i].count).attr("count_str",data[i].count_str).appendTo(block);
			$("<div/>").addClass("count").text(0).appendTo(countContainer);

			// percent container
			var percentContainer = $("<td/>").addClass("percent-container").appendTo(block);
			$("<div/>").addClass("percent hide").text(data[i].percent).appendTo(percentContainer);

			var expandExample = $("<td/>").addClass("expand-example").appendTo(block);
			$("<img/>").addClass("expand-example-btn plus-btn").attr("src","static/img/plus.png").appendTo(expandExample);
			$("<img/>").addClass("expand-example-btn minus-btn hide").attr("src","static/img/minus.png").appendTo(expandExample);
		});

		RESULT_COL = $("#result-block").find(".ngram").eq(0).find("td").length;
	}


}
function restore(p) // 89 % -> 0.89
{

	if(p.length > 0)
	{
		p = p.replace(" ","");
		if(p[0] == '<')
		{
			p = 0.01;
		}else
		{
			p = parseFloat(p.replace("%",""))/100.0;
		}
		return p;
	}else
	{
		return 0.01;
	}
}
function fill(delay)
{
	$.each($(".bar"), function(i){
		$(".bar").eq(i).animate({
			width: parseInt($(".bar").eq(i).attr("length"))
		},delay);
	});

	var _ANIMATE_COUNT = 15; 	// # of elements that perform animation, decrease the loading for client
	var _ANIMATE_DELAY = 600;	// for percentage animate delay

	$.each($(".count-container"), function(i){
		var _this = $(".count-container").eq(i);
		var _count = _this.find(".count");

		_count.countTo({
		    from: 0,
		    to: _this.attr("total"),
		    speed: delay*0.5,
		    refreshInterval: 10,
		    onComplete: function(value) {
		    	_count.text(_this.attr("count_str"));
		    	if(i > _ANIMATE_COUNT) {
		    		_this.siblings(".percent-container").find(".percent").delay(_ANIMATE_DELAY).show(0);
		    	}else {
		    		_this.siblings(".percent-container").find(".percent").slideDown(_ANIMATE_DELAY);
		    	}
		    }
		});
	});
}
function setMode()
{
	// change input style
	$("#search-bar-container").removeClass(_MODE).addClass(MODE);
	$("#search-bar").removeClass(_MODE+"-input").addClass(MODE+"-input");

	// change mode select image
	$("#"+_MODE+"-img").removeClass('hide');
	$("#"+MODE+"-img").addClass('hide');
	// change label
	$("#"+_MODE+"-label").removeClass("hide");
	$("#"+MODE+"-label").addClass("hide");

	// change convert result
	$('#cmd-convert-result').html("");


	// change UI
	// $("#mode-container").addClass("mode-margin-" + BROWSER);


	// switch speech to text input function
	if(BROWSER == "chrome") // chrome only
	{
		if(MODE == 'HLI') {
			$("#search-bar").attr("x-webkit-speech",true);
			// $("#mode-container").removeClass("no-speech").addClass("with-speech");
		}
		else {
			$("#search-bar").removeAttr("x-webkit-speech");
			// $("#mode-container").removeClass("with-speech").addClass("no-speech");
		}
	}
	else {
		$("#mode-container").addClass("no-speech");
	}


	// change examples
	$(".option-container").parent().remove();
	var ex = EXAMPLE[MODE];
	var root = $("#search-table");
	$.each(ex, function(i){
		var tr = $("<tr/>").appendTo(root);
		var td = $("<td/>").attr("idx",i).addClass("option-container hide").appendTo(tr);
		$("<div/>").addClass("option").html(ex[i]).appendTo(td);
	});

	// change help
	$("#help-container").find("table").html("");
	var hp = HELP[MODE];
	var root = $("#help-container").find("table");

	$.each(hp, function(i){
		var tr = $("<tr/>").appendTo(root);
		var key = $("<td/>").addClass("key").appendTo(tr);
		var val = $("<td/>").addClass("val").appendTo(tr);

		$.each(hp[i], function(k,v){
			$("<div/>").html(k).appendTo(key);
			$("<div/>").html(v).appendTo(val);
		});
	});
}

function infofetch()
{
	var params = location.hash.split('#');
	var q = "";

	if(params.length == 3)	// correct input format (query + mode)
	{
		// set query
		QUERY_URL = params[1];
		q = $.trim(decodeURIComponent(params[1]));

		// set mode
		if(params[2]=='HLI'){
			MODE = 'HLI';
			_MODE = 'CMD';
		}
		else {
			MODE = 'CMD';
			_MODE = 'HLI';
		}

	}else // incorrect input format
	{
		redirect("", "CMD");
	}

	// with query
	if(q.length > 0)
	{
		exampleHandler('off');				// example off
		$("#search-bar").val(q);			// perform search
		query();
	}
	// no query
	else
	{
		exampleHandler('on');				// example on
		$('#result-block').html("");		// clear result
		$('#search-bar').val('').focus();	// focus search bar
	}
}
