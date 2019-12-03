var pagina = 1;
var numeros_paginas = 0;

// Função para calcular o número de páginas necessárias
function contarTrades() {
    var max = $('#tabela-historico').attr("max");
    var temp = (max / 10);
    numeros_paginas = parseInt(temp) + 1;
    // Se for a última página desabilita o botão "Próximo"
    if(pagina >= numeros_paginas)
    {
        $(".proximo").addClass("d-none");
    }
    // Senão habilita
    else
    {
        $(".proximo").removeClass("d-none");
    }
};

// Função para atualizar o conteúdo HTML
function refresh() {
    // Realiza uma requisição AJAX do tipo GET para URL do atributo "data-url"
    $.ajax({
        url: $('#ajax-historico-transacoes').attr("data-url"),
        success: function(data) {
            $('#ajax-historico-transacoes').html(data);
        }
    });
    // Chama a função para contar os Trades
    contarTrades();
    // Chama a função para adicionar as URL nos botões
    btnAddLink();
    // A cada 5 segundos re-execute a função
    setTimeout(refresh, 5000);
};

// Função para a ação do botão
function linkBtn()
{
    // Exibe o icone
    $(this).children(".btn-right-spin").toggleClass("d-none");
    // Desabilita os botões da classe quando um botão da classe btn-action é clicado
    $(".btn-action").attr("disabled", true);
    // Pega a o atributo de ação
    var acao = this.getAttribute("acao");
    // Se for somar
    if(acao === "+")
    {
        pagina++;
    }
    // Senão se for subtrair
    else
    {
        pagina--;
    }
    // Se não for a primeira página habilita o botão "Anterior"
    if(pagina != 1)
    {
        $(".anterior").removeClass("d-none");
    }
    // Senão habilita
    else
    {
        $(".anterior").addClass("d-none");
    }
    // Pega o atributo "data-url" como link
    var temp_url = $('#ajax-historico-transacoes').attr("data-url")
    // Troca o número da página
    var url_attr = temp_url.slice(0, temp_url.length - 2) + pagina.toString() + '/';
    // Redefine o atributo URL do AJAX para a página correspondente
    $('#ajax-historico-transacoes').attr("data-url", url_attr);
    // Chama a função para recarregar o AJAX
    refresh();
    // Habilita novamente os botões
    $(".btn-action").attr("disabled", false);
    // Desabilita o icone
    $(this).children(".btn-right-spin").toggleClass("d-none");
}

// Função para redirecionar para páginas ao clicar no botão
function btnAddLink() {
    if ($('.btn-action').length > 0)
    {
        // Pega os objetos contendo a classe
        var classname = document.getElementsByClassName("btn-action");

        // Adiciona a função click para todos os objetos
        for (var i = 0; i < classname.length; i++) 
        {
            classname[i].addEventListener('click', linkBtn, false);
        }
    }
};

// Chama as funções ao carregar a página
$(function(){
    contarTrades();
    btnAddLink();
    refresh();
});
