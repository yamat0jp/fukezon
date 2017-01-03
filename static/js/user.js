/**
 * 
 */

(function(){
	$('button#ok').click(submit());
	$('button#cancel').click(function(){
		window.location = '/main'
	});
});