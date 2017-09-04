
function attachCollapseExpandEvents()
{
    $('.collapse')
        .on('show.bs.collapse', 
            function(){
                $(this).parent().find(".glyphicon-expand")
                    .removeClass("glyphicon-expand")
                    .addClass("glyphicon-collapse-down");
        })
        .on('hide.bs.collapse', 
            function(){
                $(this).parent().find(".glyphicon-collapse-down")
                    .removeClass("glyphicon-collapse-down")
                    .addClass("glyphicon-expand");
        });
}

function updateElement(sourceEl, destEl)
{
    $('#' + destEl).html($('#' + sourceEl).val())
}
