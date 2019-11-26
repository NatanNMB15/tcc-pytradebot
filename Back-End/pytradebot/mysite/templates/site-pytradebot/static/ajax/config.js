var acceptTkn = jQuery("[name=csrfmiddlewaretoken]").val();

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", acceptTkn);
        }
    }
});

// Desabilitar botão submit ao enviar um formulário válido
jQuery( function($){ 
    $.listen('parsley:form:validated', function(e){
      if (e.validationResult) {
          $('button[type=submit]').attr('disabled', 'disabled');
      }
    });
  });