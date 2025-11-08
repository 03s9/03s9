// Função de inicialização
document.addEventListener('DOMContentLoaded', function() {
    initScrollTop();
    initCountdown();
    initCartFunctionality();
    initWishlist();
    initNewsletter();
    initSmoothScroll();
    initMobileMenu();
});

// Botão Voltar ao Topo
function initScrollTop() {
    const scrollTopBtn = document.getElementById('scrollTop');

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            scrollTopBtn.classList.add('active');
        } else {
            scrollTopBtn.classList.remove('active');
        }
    });

    scrollTopBtn.addEventListener('click', function() {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
}

// Countdown Timer
function initCountdown() {
    // Define a data final (3 dias a partir de agora)
    const countDownDate = new Date().getTime() + (3 * 24 * 60 * 60 * 1000);

    const countdown = setInterval(function() {
        const now = new Date().getTime();
        const distance = countDownDate - now;

        const days = Math.floor(distance / (1000 * 60 * 60 * 24));
        const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((distance % (1000 * 60)) / 1000);

        document.getElementById('days').textContent = String(days).padStart(2, '0');
        document.getElementById('hours').textContent = String(hours).padStart(2, '0');
        document.getElementById('minutes').textContent = String(minutes).padStart(2, '0');
        document.getElementById('seconds').textContent = String(seconds).padStart(2, '0');

        if (distance < 0) {
            clearInterval(countdown);
            document.getElementById('days').textContent = '00';
            document.getElementById('hours').textContent = '00';
            document.getElementById('minutes').textContent = '00';
            document.getElementById('seconds').textContent = '00';
        }
    }, 1000);
}

// Funcionalidade do Carrinho
function initCartFunctionality() {
    let cartCount = 0;
    const cartBadge = document.querySelector('.cart-btn .badge');
    const addToCartButtons = document.querySelectorAll('.btn-add-cart');

    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            cartCount++;
            cartBadge.textContent = cartCount;

            // Animação visual
            this.innerHTML = '<i class="fas fa-check"></i> Adicionado!';
            this.style.background = 'linear-gradient(135deg, #10b981 0%, #059669 100%)';

            setTimeout(() => {
                this.innerHTML = '<i class="fas fa-shopping-cart"></i> Adicionar ao Carrinho';
                this.style.background = '';
            }, 2000);

            // Animação do badge
            cartBadge.style.transform = 'scale(1.5)';
            setTimeout(() => {
                cartBadge.style.transform = 'scale(1)';
            }, 300);

            showNotification('Produto adicionado ao carrinho!');
        });
    });

    // Click no botão do carrinho
    document.querySelector('.cart-btn').addEventListener('click', function() {
        if (cartCount > 0) {
            showNotification(`Você tem ${cartCount} item(ns) no carrinho`);
        } else {
            showNotification('Seu carrinho está vazio');
        }
    });
}

// Funcionalidade de Wishlist
function initWishlist() {
    const wishlistButtons = document.querySelectorAll('.wishlist-btn');

    wishlistButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const icon = this.querySelector('i');

            if (icon.classList.contains('far')) {
                icon.classList.remove('far');
                icon.classList.add('fas');
                this.style.color = '#ec4899';
                showNotification('Adicionado aos favoritos!');
            } else {
                icon.classList.remove('fas');
                icon.classList.add('far');
                this.style.color = '';
                showNotification('Removido dos favoritos');
            }
        });
    });
}

// Newsletter
function initNewsletter() {
    const newsletterForm = document.querySelector('.newsletter-form');

    newsletterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const email = this.querySelector('input[type="email"]').value;

        if (email) {
            showNotification('Obrigado por se inscrever! Você receberá nossas ofertas em breve.');
            this.reset();
        }
    });
}

// Smooth Scroll
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));

            if (target) {
                const headerOffset = 80;
                const elementPosition = target.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Menu Mobile
function initMobileMenu() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navMenu = document.querySelector('.nav-menu');

    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            navMenu.classList.toggle('active');
            const icon = this.querySelector('i');

            if (navMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
                navMenu.style.display = 'flex';
                navMenu.style.flexDirection = 'column';
                navMenu.style.position = 'absolute';
                navMenu.style.top = '100%';
                navMenu.style.left = '0';
                navMenu.style.right = '0';
                navMenu.style.background = 'white';
                navMenu.style.padding = '1rem';
                navMenu.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
                navMenu.style.display = '';
            }
        });
    }
}

// Função para mostrar notificações
function showNotification(message) {
    // Remove notificação existente se houver
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }

    // Cria nova notificação
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.textContent = message;

    // Estilos inline
    Object.assign(notification.style, {
        position: 'fixed',
        top: '100px',
        right: '20px',
        background: 'linear-gradient(135deg, #6366f1 0%, #ec4899 100%)',
        color: 'white',
        padding: '1rem 1.5rem',
        borderRadius: '8px',
        boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1)',
        zIndex: '9999',
        animation: 'slideIn 0.3s ease-out',
        fontWeight: '600'
    });

    document.body.appendChild(notification);

    // Remove após 3 segundos
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

// Adiciona animações CSS para notificações
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(400px);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }

    .nav-menu.active {
        animation: fadeIn 0.3s ease-out;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(-10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);

// Animação de scroll nos elementos
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
            observer.unobserve(entry.target);
        }
    });
}, observerOptions);

// Observa elementos para animação
document.addEventListener('DOMContentLoaded', function() {
    const animateElements = document.querySelectorAll('.category-card, .product-card, .section-header');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        observer.observe(el);
    });
});

// Adiciona animação fadeInUp
const fadeInStyle = document.createElement('style');
fadeInStyle.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(fadeInStyle);

// Busca (funcionalidade básica)
const searchBtn = document.querySelector('.search-btn');
if (searchBtn) {
    searchBtn.addEventListener('click', function() {
        const searchTerm = prompt('O que você está procurando?');
        if (searchTerm) {
            showNotification(`Buscando por: ${searchTerm}...`);
        }
    });
}

// Botão de usuário
const userBtn = document.querySelector('.user-btn');
if (userBtn) {
    userBtn.addEventListener('click', function() {
        showNotification('Área do usuário em desenvolvimento');
    });
}

// Adiciona efeito hover nos cards de categoria
document.querySelectorAll('.category-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-10px) scale(1.02)';
    });

    card.addEventListener('mouseleave', function() {
        this.style.transform = '';
    });
});

console.log('🛒 ShopZone Landing Page carregada com sucesso!');
