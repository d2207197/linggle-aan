function layout()
{
	// get browser size
	var s = detectBrowserSize();

	// set body
	$("body").width(s.w-20).height(s.h);

	var head = $("#header").outerHeight();
	var body = s.h-head;

	// set content and its mask
	$("#content").css("min-height",body).css("top",head-2);
	$("#content-mask").css("min-height",body).css("top",head-2).width($("#content").width()).height($("#content").height());

	// set example style
	$(".option-container").last().addClass("option-container-last");

	$("#help-container").css("left",($("#container").innerWidth() - $("#help-container").outerWidth())/2);
}