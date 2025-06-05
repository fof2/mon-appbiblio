document.addEventListener('DOMContentLoaded', function () {
    function loadStatistics() {
        fetch('/statistiques/')
            .then(response => response.json())
            .then(data => {
                document.getElementById('livres_disponibles').textContent = data.livres_disponibles;
                document.getElementById('livres_empruntes').textContent = data.livres_empruntes;
                document.getElementById('nombre_categories').textContent = data.nombre_categories;
                document.getElementById('nombre_auteurs').textContent = data.nombre_auteurs;
                document.getElementById('membres_actifs').textContent = data.membres_actifs;
                document.getElementById('emprunts_par_mois').textContent = data.emprunts_par_mois;
                document.getElementById('prix_litteraires').textContent = data.prix_litteraires;

                // Appeler la fonction animateCounter pour chaque statistique
                animateCounter('livres_disponibles', data.livres_disponibles);
                animateCounter('livres_empruntes', data.livres_empruntes);
                animateCounter('nombre_categories', data.nombre_categories);
                animateCounter('nombre_auteurs', data.nombre_auteurs);
                animateCounter('membres_actifs', data.membres_actifs);
                animateCounter('emprunts_par_mois', data.emprunts_par_mois);
                animateCounter('prix_litteraires', data.prix_litteraires);
            })
            .catch(error => console.log('Erreur lors du chargement des statistiques:', error));
    }

    // Fonction pour animer les chiffres des statistiques
    function animateCounter(elementId, targetCount) {
        const statElement = document.getElementById(elementId);
        let currentCount = 0;
        const duration = 1000;  // Durée de l'animation en ms
        const increment = targetCount / (duration / 10);  // Incrément par intervalle de 10ms

        function updateCounter() {
            if (currentCount < targetCount) {
                currentCount += increment;
                if (currentCount > targetCount) currentCount = targetCount;  // Eviter de dépasser
                statElement.textContent = Math.floor(currentCount);
                requestAnimationFrame(updateCounter);
            }
        }

        requestAnimationFrame(updateCounter);
    }

    // Charger les statistiques au démarrage
    loadStatistics();
});
