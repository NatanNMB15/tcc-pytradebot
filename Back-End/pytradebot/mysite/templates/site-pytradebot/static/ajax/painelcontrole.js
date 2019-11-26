function refresh() {
    $.ajax({
        url: $('#ajax-painel-controle').attr("data-url"),
        success: function(data) {
            $('#ajax-painel-controle').html(data);
            btnAddLink();
        }
    });
    setTimeout(refresh, 10000);
};
$(function(){
    refresh();
});
