(function($){
    $("#bs-toggle-btn").click(function(){
        $('#bs-modal').show(1000);
    })

    $('.close').click(function(){
        $('#bs-modal').slideUp(1000);
    })

})(jQuery);

const modal = document.querySelector('#bs-modal');

window.onclick = ev =>{
    if (ev.target == modal){
        modal.style.display = "none";
    }
}
