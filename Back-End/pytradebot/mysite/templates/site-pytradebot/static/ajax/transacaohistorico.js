function refresh() {
    $.ajax({
        url: $('#ajax-historico-transacoes').attr("data-url"),
        success: function(data) {
            $('#ajax-historico-transacoes').html(data);
        }
    });
    setTimeout(refresh, 5000);
};
$(function(){
    refresh();
});