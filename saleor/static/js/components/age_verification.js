import React from 'react';

export default $(document).ready((e) => {
  $(window).ready(function ($) {

    if (sessionStorage.getItem('advertOnce') !== 'true') {
      //sessionStorage.setItem('advertOnce','true');
      $('.box').removeAttr('hidden');
      $('.box').show();
    } else {
      $('.box').hide();
      $('.overlay-verify').hide();
    }

    $('#refresh-page').on('click', function () {
      $('.box').hide();
      $('.overlay-verify').hide();
      sessionStorage.setItem('advertOnce', 'true');
    });

    $('#reset-session').on('click', function () {
      $('.box').show();
      sessionStorage.setItem('advertOnce', '');
    });

  });
})
