var latomezok = 5;
var process_id = 0;
var remoted = [];
var latomezok_li = [1, 2, 3, 4, 5];
$(document).ready(function(){
	$("#dow").click(function(){
		var star_name = $("#starname").val();
        if(star_name.includes(",")){
            
        }
        star_name = star_name.replace(" ", "+");
        var dpi = $("#resolution").val();
        var taj_norm = $('#normal').is(":checked");
        var taj_zenit = $('#zenit').is(":checked");
        var taj_newton = $('#newton').is(":checked");
        console.log(star_name + " " + dpi + " " + taj_norm);
        var fovs = [];
        for (let i = 0; i < latomezok; i++) {
            if(remoted.indexOf(i+1) == -1){
                var id = "#" + (i+1) + "_fov";
                fovs.push($(id).val());
            }
        }
        console.log(fovs);
        var mags = [];
        for (let i = 0; i < latomezok; i++) {
            if(remoted.indexOf(i+1) == -1){
                var id = "#" + (i+1) + "_mag";
                mags.push($(id).val());
            }
        }
        console.log(mags);

        process_bar(taj_norm, taj_zenit, taj_newton, star_name, dpi, fovs, mags);
        process_id = 0;
        if(taj_norm){
            var iterator = 0;
            var utotag = "";
            dow(iterator, fovs, mags, star_name, dpi, utotag, taj_norm, taj_zenit, taj_newton);
        }else if(taj_zenit){
            var iterator = 0;
            var utotag = "&east=left";
            taj_zenit = false;
            dow(iterator, fovs, mags, star_name, dpi, utotag, taj_norm, taj_zenit, taj_newton);
        }else if(taj_newton){
            var iterator = 0;
            var utotag = "&east=left&north=down";
            taj_newton = false;
            dow(iterator, fovs, mags, star_name, dpi, utotag, taj_norm, taj_zenit, taj_newton);
        }
	});

    $(".close").click(function(){
        var id = $(this).data("lato");
        console.log(id);
        var elemek = $(".latomezo");
        var index = latomezok_li.indexOf(id);
        latomezok_li.splice(index, 1); 
        for(let i = 0; i < elemek.length; i++){
            if($(elemek[i]).data("lato") == id){
                $(elemek[i]).remove();
            }
            if($(elemek[i]).data("lato") > id && $(elemek[i]).data("type") == "text"){
                text = "Látómező " + (latomezok_li.indexOf($(elemek[i]).data("lato"))+1) + ".";
                $(elemek[i]).empty();
                $(elemek[i]).append(text);
            }
        }
        remoted.push((id));
        console.log(remoted);
    });
});

function process_bar(taj_norm, taj_zenit, taj_newton, star_name, dpi, fovs, mags){
    var html = "";
    var counter = 1;
    var name = star_name.replace('+', ' ');
    if(taj_norm){
        var taj = "Normál tájolás"
        for(let i = 0; i < fovs.length; i++){
            html += "<tr><td>" + name + " - " + taj + " - " + dpi + "DPI - " + fovs[i] + "' - " + mags[i] + "m</td><td><div class='pause' id='process_" + counter + "'></div></td></tr>"
            counter++;
        }
    }

    if(taj_zenit){
        var taj = "Zenit tükrős tájolás"
        for(let i = 0; i < fovs.length; i++){
            html += "<tr><td>" + name + " - " + taj + " - " + dpi + "DPI - " + fovs[i] + "' - " + mags[i] + "m</td><td><div class='pause' id='process_" + counter + "'></div></td></tr>"
            counter++;
        }
    }

    if(taj_newton){
        var taj = "Newton tájolás"
        for(let i = 0; i < fovs.length; i++){
            html += "<tr><td>" + name + " - " + taj + " - " + dpi + "DPI - " + fovs[i] + "' - " + mags[i] + "m</td><td><div class='pause' id='process_" + counter + "'></div></td></tr>"
            counter++;
        }
    }

    $("#process_bar").empty();
    $("#process_bar").append(html);
}

function load_process(n){
    var id = "#process_" + n;
    $(id).removeClass("pause").addClass("loading");
}

function success_process(n){
    var id = "#process_" + n;
    $(id).removeClass("loading").addClass("success");
}

function error_process(n){
    var id = "#process_" + n;
    $(id).removeClass("loading").addClass("error");
}

function dow(i, fovs, mags, star_name, dpi, utotag, taj_norm, taj_zenit, taj_newton){
	var url = "image_dow?name=" +
    star_name + "&fov=" +
    fovs[i] + "&maglimit=" +
    mags[i] + "&resolution=" + dpi +
    utotag;
    process_id++;
    load_process(process_id);
    $.get(url,
        function(data,status){
            d = JSON.parse(data);
            console.log(d.status);
            if (d.status){
                success_process(process_id);
            }else{
                error_process(process_id);
            }
            console.log(url + " " + data);
    }).fail(function() {
        error_process(process_id);
    }).always(function() {
        if(i+1 < fovs.length){
            dow(i+1, fovs, mags, star_name, dpi, utotag, taj_norm, taj_zenit, taj_newton);
        }else{
            taj(fovs, mags, star_name, dpi, taj_norm, taj_zenit, taj_newton);
        }
    });
}

function taj(fovs, mags, star_name, dpi, taj_norm, taj_zenit, taj_newton){
    taj_norm = false;
    if(taj_zenit){
        var iterator = 0;
        var utotag = "&east=left";
        taj_zenit = false;
        dow(iterator, fovs, mags, star_name, dpi, utotag, taj_norm, taj_zenit, taj_newton);
    }else if(taj_newton){
        taj_zenit = false;
        var iterator = 0;
        var utotag = "&east=left&north=down";
        taj_newton = false;
        dow(iterator, fovs, mags, star_name, dpi, utotag, taj_norm, taj_zenit, taj_newton);
    }
}