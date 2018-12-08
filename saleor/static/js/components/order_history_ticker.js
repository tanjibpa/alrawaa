export default $(document).ready((e) => {
  $(window).ready(function ($) {

    var i = 0;
    function loop(orders_texts) {
      if ($(".order-history-text")) {
        $(".order-history-text").remove();
      }
      if (orders_texts[i]) {
        $("#order-history-ticker").append("<p class='order-history-text'>" + orders_texts[i] + "</p>");
      }
      if (++i < orders_texts.length) {
        setTimeout(loop, 3000, orders_texts);
      }
      else {
        i = 0;
        setTimeout(loop, 3000, orders_texts);
      }
    }

    function getOrdersText() {
      $.ajax({url: '/order/order_history'})
      .done(function (orders) {
        var orders_texts = orders["orders"];
        localStorage.setItem('order_texts_cache', orders_texts);
        loop(orders_texts);
      })
    }

    var orders_text_expire = localStorage.getItem('orders_text_expire');
    var order_texts_cache = localStorage.getItem('order_texts_cache');
    if (!order_texts_cache) {
      console.log("Here1");
      var now = new Date().getTime();
      localStorage.setItem('orders_text_expire', now);
      getOrdersText();
    }
    else if (order_texts_cache) {
      var now = new Date().getTime();
      if ((now - parseInt(orders_text_expire)) < 60*60*1000) {
        var order_texts_array = order_texts_cache.split(',');
        console.log("Here2");
        loop(order_texts_array);
      }
      else {
        console.log("here3");
        var now = new Date().getTime();
        localStorage.setItem('orders_text_expire', now);
        getOrdersText();
      }
    }
  });
})
