// Função para redirecionar para páginas ao clicar no botão
if ($('.btn-link-js').length > 0)
{
   function linkBtn()
   {
      // Pega o atributo "data-url" como link
      var url = this.getAttribute("data-url");
      // Redireciona o usuário para a página do atributo
      window.location.href = url;
   }
   // Pega os objetos contendo a classe
   var classname = document.getElementsByClassName("btn-link-js");

   // Adiciona a função click para todos os objetos
   for (var i = 0; i < classname.length; i++) 
   {
      classname[i].addEventListener('click', linkBtn, false);
   }
}