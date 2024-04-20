window.onload = () => {
    document.getElementById('submit').onclick = () => {
        var phototval = new XMLHttpRequest();
        phototval.open('POST', "/subm?name=" + document.getElementById('name').value + '&fullname=' + document.getElementById('FIO').value
        + "&email=" + document.getElementById('email').value + "&text=" + document.getElementById('text').value, true);
        phototval.send();
        alert('Ваша заявка успешно создана!');
    }
}