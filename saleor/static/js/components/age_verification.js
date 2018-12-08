export default $(document).ready((e) => {
  $(window).ready(function ($) {

    if (!localStorage.getItem('ageVerified')) {
      //sessionStorage.setItem('advertOnce','true');
      $('.box').removeAttr('hidden');
      // $('.box').show();
      $('.overlay-verify').removeAttr('hidden');
    } else {
      $('.box').hide();
      $('.overlay-verify').hide();
    }

    $('#refresh-page').on('click', function () {
      $('.box').hide();
      $('.overlay-verify').hide();
      localStorage.setItem('ageVerified', 'true');
    });

    $('#reset-session').on('click', function () {
      $('.box').show();
      localStorage.removeItem('ageVerified');
    });

  });
})
