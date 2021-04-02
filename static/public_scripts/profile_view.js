// Notification
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

// For amount transfer amount output display
var amountOutput = document.getElementById('amountOutput')
var amount = document.getElementById('amount')
var convertAmount = new Intl.NumberFormat('en-NG', {
        style: 'currency',
        currency: 'NGN'
    })

amount.addEventListener('keyup', function(){
    var output = amount.value
    amountOutput.innerHTML = convertAmount.format(output)
    amountOutput.style.fontSize = '2rem'

    let payBtn = document.getElementById('bs-pay')
    if (amount.value >= 100){
        payBtn.classList.remove('disabled')
        payBtn.style.cursor = "pointer"
    }else{
        payBtn.classList.add('disabled')
        payBtn.style.cursor = "not-allowed"
    }
})

// for Web referal code click to copy to clickboard
function clickToCopyWebReferal(){
    let myInput = document.getElementById('bs-web-referal-code')

    myInput.select();
    myInput.setSelectionRange(0, 99999, "forward")
    document.execCommand('copy')
    alert('copied to clip board')
}