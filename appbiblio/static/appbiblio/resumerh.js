document.querySelectorAll('.toggle-resume-btn').forEach(button => {
    button.addEventListener('click', () => {
        const livreId = button.getAttribute('data-id');
        const resumeDiv = document.getElementById(`resume-${livreId}`);
        if (resumeDiv.style.display === 'none' || resumeDiv.style.display === '') {
            resumeDiv.style.display = 'block';
            button.textContent = 'Cacher le résumé';
        } else {
            resumeDiv.style.display = 'none';
            button.textContent = 'Voir le résumé';
        }
    });
});




