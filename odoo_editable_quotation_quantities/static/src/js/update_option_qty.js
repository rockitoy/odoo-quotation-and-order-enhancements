$( document ).ready(function() {
var quote_div = window.location.pathname
var word = '/my/orders'
if (quote_div.includes(word)){
$.ajax({
      url: '/get_all_options',
      type: 'GET',
      data: {},
      success: function(response) {
      if(response){
      var data = JSON.parse(response);
      $.each(data, function(key, value) {
      var class_op = ".option_"+value.id;
      var class_plus = ".plus_option_"+value.id;
      $(class_op).click(function(){
      var qty = $('.option_qty_inp_'+value.id).val();
      var option_id = $(this).attr("data-option-id");
      var new_qty = --qty;
      var float = parseFloat(new_qty).toFixed(1);
      $('.option_qty_inp_'+value.id).val(float);
      $.ajax({
      url: '/update_option_qty',
      type: 'GET',
      data: {
        qty: new_qty,
        op_id : option_id
      },
      success: function(response) {
      if(response == 'fail'){
      location.reload();
      }
      else{
      $('.span_option_qty_'+value.id).text(response);

      }

      },
    });

      });
      $(class_plus).click(function(){
      var qty = $('.option_qty_inp_'+value.id).val();
      var option_id = $(this).attr("data-option-id");
      var new_qty = ++qty;
       var float = parseFloat(new_qty).toFixed(1);
     $('.option_qty_inp_'+value.id).val(float);
      $.ajax({
      url: '/update_option_qty',
      type: 'GET',
      data: {
        qty: new_qty,
        op_id : option_id
      },
      success: function(response) {
      if(response == 'fail'){
      location.reload();
      }
      else{
      $('.span_option_qty_'+value.id).text(response);

      }
      },
    });
      });
        });
       }
      },
    });
}
else{
console.log("NO")
}

});
