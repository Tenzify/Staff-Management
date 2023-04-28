document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('add-staff-form').addEventListener('submit', function (event) {
        event.preventDefault();

        const ign = document.getElementById('ign').value;
        const rank = document.getElementById('rank').value;

        fetch('/add_staff', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `ign=${encodeURIComponent(ign)}&rank=${encodeURIComponent(rank)}`
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                console.error("Error al agregar miembro");
            }
        })
        .catch(error => console.error(error));
    });

    async function handlePromoteDemote(event, action, id) {
        event.preventDefault();
    
        // Obtener la fecha actual
        const currentDate = new Date().toISOString().slice(0, 19).replace("T", " ");
    
        // Promover o degradar al miembro del staff
        const response = await fetch(`/${action}_staff`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `id=${encodeURIComponent(id)}`
        });
    
        if (response.ok) {
            // Actualizar la fecha de la última promoción en la base de datos
            const updateResponse = await fetch("/update_last_promotion", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: `id=${encodeURIComponent(id)}&date=${encodeURIComponent(currentDate)}`
            });
    
            if (updateResponse.ok) {
                // Actualizar la fecha de la última promoción en la tabla HTML
                document.querySelector(`tr[data-id='${id}'] .last-promotion`).textContent = currentDate;
            } else {
                console.error("Error al actualizar la fecha de la última promoción");
            }
    
            location.reload();
        } else {
            console.error("Error al actualizar rango");
        }
    }

    function handleDelete(event, id) {
        event.preventDefault();
        fetch(`/delete_staff`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: `id=${encodeURIComponent(id)}`
        })
        .then(response => {
            if (response.ok) {
                location.reload();
            } else {
                console.error("Error al eliminar miembro");
            }
        })
        .catch(error => console.error(error));
    }

    const promoteButtons = document.querySelectorAll('.promote-button');
    const demoteButtons = document.querySelectorAll('.demote-button');
    const deleteButtons = document.querySelectorAll('.delete-button');

    promoteButtons.forEach(button => {
        button.addEventListener('click', (event) => handlePromoteDemote(event, 'promote', button.dataset.id));
    });

    demoteButtons.forEach(button => {
        button.addEventListener('click', (event) => handlePromoteDemote(event, 'demote', button.dataset.id));
    });

    deleteButtons.forEach(button => {
        button.addEventListener('click', (event) => handleDelete(event, button.dataset.id));
    });

    function getCurrentDate() {
        let date = new Date();
        let day = String(date.getDate()).padStart(2, '0');
        let month = String(date.getMonth() + 1).padStart(2, '0');
        let year = date.getFullYear();
        return `${year}-${month}-${day}`;
    }


    
});
