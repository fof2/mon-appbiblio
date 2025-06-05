document.addEventListener('DOMContentLoaded', () => {
  // Sélectionne tous les boutons "Voir plus"
  document.querySelectorAll('.toggle-summary').forEach(button => {
    button.addEventListener('click', () => {
      const summaryEl = button.previousElementSibling;
      const fullText = summaryEl.dataset.fulltext;

      if (button.textContent.trim() === 'Voir plus') {
        summaryEl.textContent = fullText; // afficher résumé complet
        button.textContent = 'Voir moins';
      } else {
        // Tronquer à 200 caractères
        let shortText = fullText.slice(0, 200);
        if (fullText.length > 200) {
          shortText += '...';
        }
        summaryEl.textContent = shortText;
        button.textContent = 'Voir plus';
      }
    });
  });
});
