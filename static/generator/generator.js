$(document).ready(function () {
    // for dynamic content
  $(document).on('click', '.fa-chevron-down, .fa-chevron-up',function () {
    if($(this).hasClass('fa-chevron-down')){
        $(this).removeClass('fa-chevron-down').addClass('fa-chevron-up');
    }
    else{
        $(this).removeClass('fa-chevron-up').addClass('fa-chevron-down');
    }
    if($(this).parent().next('.inner_v').length > 0){
        $('.inner_v').toggleClass('visible');
    }
    if($(this).parent().next('.inner_m').length > 0){
        $('.inner_m').toggleClass('visible');
    }
});
  $(document).on('click', '.fa.fa-times', function (e){
      e.stopPropagation();
      $('.popupWrapper').css('display','none');
      var selected = $('.fc-head').find('.ui-selected');
        $(selected).each(function () {
            $(this).removeClass('ui-selected');
        })
  });
});
