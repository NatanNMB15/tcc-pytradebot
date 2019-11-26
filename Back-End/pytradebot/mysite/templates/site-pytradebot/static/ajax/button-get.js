// Função para redirecionar para páginas ao clicar no botão
function btnAddLink() {
    if ($('.btn-action').length > 0)
    {
        function linkBtn()
        {
            // Exibe o icone
            $(this).children(".btn-right-spin").toggleClass("d-none");
            // Desabilita os botões da classe quando um botão da classe btn-action é clicado
            $(".btn-action").attr("disabled", true);
            // Pega o atributo "data-url" como link
            var url_attr = this.getAttribute("data-url");
            // Chama a URL
            $.ajax({
                type: 'GET',
                url: url_attr,
                success: function(data) {
                }
            });
        }
        // Pega os objetos contendo a classe
        var classname = document.getElementsByClassName("btn-action");

        // Adiciona a função click para todos os objetos
        for (var i = 0; i < classname.length; i++) 
        {
            classname[i].addEventListener('click', linkBtn, false);
        }
    }
};