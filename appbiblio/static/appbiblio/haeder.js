
    document.addEventListener('DOMContentLoaded', function () {
        let currentSlide = 0;
        const slides = document.querySelectorAll('.hero-bg');
        const dots = document.querySelectorAll('.slider-dot');

        function showSlide(index) {
            slides.forEach((slide, i) => {
                slide.classList.toggle('active', i === index);
                dots[i].classList.toggle('active', i === index);
            });
        }

        function nextSlide() {
            currentSlide = (currentSlide + 1) % slides.length;
            showSlide(currentSlide);
        }

        setInterval(nextSlide, 4000); // toutes les 4 secondes
    });

    document.addEventListener('DOMContentLoaded', function() {
    const backgrounds = document.querySelectorAll('.hero-bg');
    const dots = document.querySelectorAll('.slider-dot');
    let currentIndex = 0;
    
    function changeBackground() {
        backgrounds.forEach(bg => bg.classList.remove('active'));
        dots.forEach(dot => dot.classList.remove('active'));
        
        currentIndex = (currentIndex + 1) % backgrounds.length;
        
        backgrounds[currentIndex].classList.add('active');
        dots[currentIndex].classList.add('active');
    }
    
    // Change toutes les 5 secondes
    setInterval(changeBackground, 5000);
    
    // Gestion des clics sur les indicateurs
    dots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            backgrounds.forEach(bg => bg.classList.remove('active'));
            dots.forEach(d => d.classList.remove('active'));
            
            currentIndex = index;
            backgrounds[currentIndex].classList.add('active');
            dot.classList.add('active');
        });
    });
});

