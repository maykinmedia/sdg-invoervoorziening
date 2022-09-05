async function resendInvite(pk, subpath="") {
    const url = `${window.location.origin}${subpath}/admin/resend_invite`
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    const headers = {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
    }

    const body = {
        pk
    }

    response = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
        mode: 'same-origin'
    })
        .then(response => response.status)

    switch(await response) {
        case 200:
            alert("De email is opnieuw verstuurd");
            break;
        case 204:
            alert("De uitnodiging is all geaccepteerd.");
            break;
        default:
            alert("Er is iets fout gegaan met het opniew versturen, probeer later opnieuw.");
    }
};
