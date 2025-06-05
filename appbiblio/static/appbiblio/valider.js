
  document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("form-panier");
    form.addEventListener("submit", function (e) {
      e.preventDefault(); // Empêche l'envoi immédiat
      alert("Commande validée !");
      form.submit(); // Envoie le formulaire après l'alerte
    });
  });

  <!-- suppression panier -->

  function confirmerSuppression(event) {
    if (!confirm("Êtes-vous sûr de vouloir supprimer cet article du panier ?")) {
      event.preventDefault();
    }
  }



