function verificarSimulacao()
{
   // Ao marcar o modo de simulação desativa chave API e chave secreta
   if ($('#id_simulacao').is(':checked'))
   {
      $('#chave_api').addClass("d-none");
      $('#chave_api').find("label").removeClass("field-required");
      $('#chave_secreta').addClass("d-none");
      $('#chave_secreta').find("label").removeClass("field-required");
   }
   // Senão ativa chave API e chave secreta
   else
   {
      $('#chave_api').removeClass("d-none");
      $('#chave_api').find("label").addClass("field-required");
      $('#chave_secreta').removeClass("d-none");
      $('#chave_secreta').find("label").addClass("field-required");
   }
}

// Ao clicar no input de modo de simulação execute a função abaixo
$("#id_simulacao").click(function() {
   verificarSimulacao();
});

// Verifica se a simulação já está ativada ou não ao carregar a página
$(document).ready(function(){
   verificarSimulacao();
 });