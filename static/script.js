function checknum() {
    if(/^[0-9]+$/.test(document.getElementById('pay-amt').value) === false) {
        alert("The amount should be numerical");
        return false;
    }
    if(document.getElementById('gym-id').value === '')
    {
        alert('Choose an option from Gym ID')
        return false;
    }
    return true
} 
function checknum1() {
    if(/^[0-9]+$/.test(document.getElementById('pay-amt').value) === false) {
        alert("The amount should be numerical");
        return false;
    }
}

function checkopts() {
    if(document.getElementById('payment-id').value === '') {
        alert('Select an option from payment ID');
        return false;
    }
    else if(/^[0-9]{10}$/.test(document.getElementById('mobile-number').value) === false) {
        alert("Phone number should be 10 digit number");
        return false;    
    }
    return true;
}
function checkamt() {
    if(/[0-9]+/.test(document.getElementById('age').value) === false) {
        alert("The age should be numerical");
        return false;
    }
    else if(/^[0-9]{10}$/.test(document.getElementById('mobno').value) === false) {
        alert("Phone number should be 10 digit number");
        return false;
    }
    else if(document.getElementById('pay-id').value === '') {
        alert('Select an option from payment ID');
        return false;
    }
    else if(document.getElementById('trainer-id').value === '') {
        alert('Select an option from trainer ID');
        return false;
    }
    return true;
}
function ask() {
    return confirm('Are you sure you want to delete?')
}
