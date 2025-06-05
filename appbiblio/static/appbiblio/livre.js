// Exemple de mise à jour dynamique du nombre de livres
$(document).ready(function() {
    $.ajax({
        url: "{% url 'livres_disponibles_ajax' %}",
        method: "GET",
        success: function(data) {
            $(".stat-number").text(data.livres_disponibles); // Met à jour la valeur dans la section Statistiques
        }
    });
});


document.querySelectorAll('.category-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        const nomCategorie = this.dataset.category;
        fetch(`/api/livres/${nomCategorie}/`)
            .then(res => res.json())
            .then(data => {
                const container = document.getElementById('books-container');
                container.innerHTML = '';
                data.livres.forEach(livre => {
                    container.innerHTML += `
                        <div class="book-card" style="width: 220px;">
                            <div class="book-cover">
                                <img src="${livre.couverture}" alt="Couverture du livre ${livre.titre}">
                                <div class="book-overlay"></div>
                                <div class="book-category">${livre.categorie}</div>
                            </div>
                            <div class="p-3">
                                <h3 class="book-title">${livre.titre}</h3>
                                <p class="book-author">${livre.auteur}</p>
                                <div class="book-meta mb-3">
                                    <div class="book-meta-item">
                                        <i class="fas fa-dollar-sign me-1"></i> <span>${livre.prix}</span>
                                    </div>
                                    <div class="book-meta-item">
                                        <i class="fas fa-book-open me-1"></i> <span>${livre.statut}</span>
                                    </div>
                                </div>
                                <button class="btn btn-primary btn-sm w-100 btn-reserve" data-book-id="${livre.id}">
                                    ${livre.statut === 'disponible' ? 'Réserver' : 'Emprunter'}
                                </button>
                            </div>
                        </div>`;
                });
                document.getElementById("featured-title").textContent = `Livres en Vedette - ${nomCategorie}`;
            });
    });
});
document.addEventListener('DOMContentLoaded', function() {
    const scrollLeftButton = document.getElementById('scroll-left');
    const scrollRightButton = document.getElementById('scroll-right');
    const booksContainer = document.getElementById('books-container');

    scrollLeftButton.addEventListener('click', function() {
        booksContainer.scrollBy({ left: -220, behavior: 'smooth' });
    });

    scrollRightButton.addEventListener('click', function() {
        booksContainer.scrollBy({ left: 220, behavior: 'smooth' });
    });

    // Activer/désactiver les boutons en fonction de la position de défilement
    booksContainer.addEventListener('scroll', function() {
        scrollLeftButton.disabled = booksContainer.scrollLeft === 0;
        scrollRightButton.disabled = booksContainer.scrollLeft + booksContainer.clientWidth >= booksContainer.scrollWidth;
    });
});
$(document).ready(function() {
    // Initialiser l'animation CounterUp
    $('.stat-number').counterUp({
        delay: 10, // Temps entre chaque incrément
        time: 1000 // Durée totale de l'animation
    });
});
   // our le bouton voir resumer du livre
    document.querySelectorAll('.toggle-resume-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.dataset.id;
            const resumeDiv = document.getElementById(`resume-${id}`);
            if (resumeDiv.style.display === 'none') {
                resumeDiv.style.display = 'block';
                this.textContent = 'Masquer le résumé';
            } else {
                resumeDiv.style.display = 'none';
                this.textContent = 'Voir le résumé';
            }
        });
    });

