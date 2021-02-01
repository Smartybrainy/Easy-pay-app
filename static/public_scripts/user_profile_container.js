(function($){
    $("#bs-toggle-btn").click(function(){
        $('#bs-modal').show("fast");
    })

    $('.close').click(function(){
        $('#bs-modal').slideUp("fast");
    })

})(jQuery);

const modal = document.querySelector('#bs-modal');

window.onclick = ev =>{
    if (ev.target == modal){
        modal.style.display = "none";
    }
}
