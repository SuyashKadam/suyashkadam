// Live banner deploy time
const deployTimeEl = document.getElementById('deploy-time');
if (deployTimeEl) {
  const now = new Date();
  deployTimeEl.textContent = `Deployed ${now.toUTCString()}`;
}

// Navbar scroll effect
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 50);
});

// Hamburger menu
const hamburger = document.getElementById('hamburger');
hamburger?.addEventListener('click', () => {
  document.querySelector('.nav-links').classList.toggle('mobile-open');
});

// Typed text animation
const phrases = [
  'Senior DevOps Engineer',
  'AWS Cloud Architect',
  'Infrastructure Automation Expert',
  'Terraform Specialist',
  'ECS & Kubernetes Engineer',
];
let phraseIdx = 0, charIdx = 0, deleting = false;
const typedEl = document.getElementById('typed');

function type() {
  if (!typedEl) return;
  const phrase = phrases[phraseIdx];
  if (deleting) {
    typedEl.textContent = phrase.substring(0, --charIdx);
  } else {
    typedEl.textContent = phrase.substring(0, ++charIdx);
  }
  if (!deleting && charIdx === phrase.length) {
    setTimeout(() => { deleting = true; setTimeout(type, 50); }, 2000);
    return;
  }
  if (deleting && charIdx === 0) {
    deleting = false;
    phraseIdx = (phraseIdx + 1) % phrases.length;
  }
  setTimeout(type, deleting ? 40 : 75);
}
type();

// Floating particles
const particleContainer = document.getElementById('particles');
if (particleContainer) {
  for (let i = 0; i < 30; i++) {
    const p = document.createElement('div');
    p.style.cssText = `
      position:absolute;
      width:${Math.random()*3+1}px;
      height:${Math.random()*3+1}px;
      background:rgba(0,212,255,${Math.random()*0.4+0.1});
      border-radius:50%;
      left:${Math.random()*100}%;
      top:${Math.random()*100}%;
      animation:float ${Math.random()*8+6}s ease-in-out infinite;
      animation-delay:-${Math.random()*6}s;
    `;
    particleContainer.appendChild(p);
  }
}

// Add float keyframes dynamically
const style = document.createElement('style');
style.textContent = `
  @keyframes float {
    0%,100%{transform:translateY(0) translateX(0);}
    33%{transform:translateY(-20px) translateX(10px);}
    66%{transform:translateY(10px) translateX(-10px);}
  }
  .mobile-open {
    display:flex!important;
    flex-direction:column;
    position:fixed;
    top:70px;left:0;right:0;
    background:rgba(10,10,15,0.98);
    padding:24px;
    gap:20px;
    border-bottom:1px solid rgba(255,255,255,0.08);
  }
`;
document.head.appendChild(style);

// Intersection observer for animations
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.style.opacity = '1';
  });
}, { threshold: 0.1 });

document.querySelectorAll('.about-card, .skill-category, .arch-box, .contact-info')
  .forEach(el => {
    el.style.transition = 'opacity 0.6s ease, transform 0.3s ease';
    el.style.opacity = '0';
    setTimeout(() => el.style.opacity = '1', 100);
    observer.observe(el);
  });
