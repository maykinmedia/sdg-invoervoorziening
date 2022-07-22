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

    await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(body),
        mode: 'same-origin'
    })
        .then(response => console.log(response.status))
};
