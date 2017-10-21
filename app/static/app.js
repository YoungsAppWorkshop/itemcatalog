$(document).ready(function () {
  $('[data-toggle="offcanvas"]').click(function () {
    $('.row-offcanvas').toggleClass('active');
  });
  if (window.location.pathname.split('/')[2] == 'categories') {
    var current_category = window.location.pathname.split('/')[3];
    var current_category_name = $('#sidebar').find('[data-category-id="' + current_category + '"]').text();
    $('#sidebar').find('[data-category-id="' + current_category + '"]').addClass('active');
    $('.category-info').find('h1').text(current_category_name);
  }
});

// Temporary Bug Fix for facebook log in redirect url leaves #_=_
if (window.location.hash && window.location.hash == '#_=_') {
        window.location.hash = '';
}
