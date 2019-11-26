// Aplicar máscara de dados nos campos necessários
jQuery( function($){  
  $('[data-mask]').each(function() {
    $(this).mask($(this).attr("data-mask"));
  });
});

// Aplicar alteração de número de telefone de 8 dígitos para 9 dígitos
jQuery( function($){  
  $("#id_telefone").mask('(00)0000-00000', incluiDigito);
});

// Função para realizar a alteração de número de telefone de 8 dígitos para 9 dígitos
var incluiDigito = {
  onKeyPress: function (phone, e, field, options) {
      var masks = ['(00)0000-00000', '(00)00000-0000'];
      var mask = (phone.length > 13) ? masks[1] : masks[0];
      $('#id_telefone').mask(mask, options);
  }
};
