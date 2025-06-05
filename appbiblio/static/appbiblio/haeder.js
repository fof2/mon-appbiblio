
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

