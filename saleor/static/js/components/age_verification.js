export default $(document).ready((e) => {
  $(window).ready(function ($) {

    if (sessionStorage.getItem('ageVerified') == 'true') {
      //sessionStorage.setItem('advertOnce','true');
      $('.box').hide();
      $('.overlay-verify').hide();
    } else {
      $('.box').removeAttr('hidden');
      $('.box').show();
    }

    $('#refresh-page').on('click', function () {
      $('.box').hide();
      $('.overlay-verify').hide();
      sessionStorage.setItem('ageVerified', 'true');
    });

    $('#reset-session').on('click', function () {
      $('.box').show();
      sessionStorage.setItem('ageVerified', '');
    });

  });
})
