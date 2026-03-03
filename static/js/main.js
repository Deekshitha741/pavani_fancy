// ══════════════════════════════════════════
//  SRI PAVANI JEWELLERY — MAIN JS
// ══════════════════════════════════════════

// ── THEME ──
const html = document.documentElement;
const themeToggle = document.getElementById('themeToggle');
const themeIcon = document.getElementById('themeIcon');

const savedTheme = localStorage.getItem('sp-theme') || 'dark';
html.setAttribute('data-theme', savedTheme);
updateThemeIcon(savedTheme);

if (themeToggle) {
  themeToggle.addEventListener('click', () => {
    const current = html.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('sp-theme', next);
    updateThemeIcon(next);
  });
}

function updateThemeIcon(theme) {
  if (!themeIcon) return;
  themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

// ── MOBILE MENU ──
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const closeMenu = document.getElementById('closeMenu');
const overlay = document.getElementById('overlay');

if (hamburger) {
  hamburger.addEventListener('click', () => {
    mobileMenu.classList.add('open');
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  });
}
if (closeMenu) {
  closeMenu.addEventListener('click', closeMobileMenu);
}
if (overlay) {
  overlay.addEventListener('click', closeMobileMenu);
}
function closeMobileMenu() {
  if (mobileMenu) mobileMenu.classList.remove('open');
  if (overlay) overlay.classList.remove('active');
  document.body.style.overflow = '';
}

// ── PARTICLES ──
function createParticles() {
  const container = document.querySelector('.hero-particles');
  if (!container) return;
  for (let i = 0; i < 25; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = Math.random() * 100 + '%';
    p.style.width = p.style.height = (Math.random() * 3 + 1) + 'px';
    p.style.animationDuration = (Math.random() * 10 + 8) + 's';
    p.style.animationDelay = (Math.random() * 8) + 's';
    container.appendChild(p);
  }
}
createParticles();

// ── ADD TO CART ──
function isLoggedIn() {
  return document.body.dataset.loggedIn === 'true';
}

function addToCart(productId, btn) {
  if (!isLoggedIn()) {
    document.getElementById('loginModal').classList.add('active');
    return;
  }

  btn.disabled = true;
  btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

  fetch(`/cart/add/${productId}`, {
    method: 'POST',
    headers: { 'X-Requested-With': 'XMLHttpRequest' }
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      // Update badge
      const badge = document.getElementById('cartBadge');
      if (badge) badge.textContent = data.cart_count;

      // Show quantity controls
      const controls = btn.closest('.cart-controls, .product-footer');
      if (controls) {
        const qtyWrap = controls.querySelector('.qty-wrap');
        if (qtyWrap) {
          btn.style.display = 'none';
          qtyWrap.style.display = 'flex';
        }
      }

      showToast('Added to cart!', 'success');
    } else {
      showToast(data.message || 'Error adding to cart', 'error');
    }
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-plus"></i> Add';
  })
  .catch(() => {
    showToast('Something went wrong', 'error');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-plus"></i> Add';
  });
}

function updateQty(itemId, action, displayEl) {
  fetch(`/cart/update/${itemId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-Requested-With': 'XMLHttpRequest'
    },
    body: `action=${action}`
  })
  .then(r => r.json())
  .then(data => {
    if (data.success) {
      if (data.removed) {
        const card = displayEl.closest('.cart-item');
        if (card) card.remove();
        // update badge
        const badge = document.getElementById('cartBadge');
        if (badge) badge.textContent = Math.max(0, parseInt(badge.textContent || '0') - 1);
      } else if (displayEl) {
        displayEl.textContent = data.quantity;
      }
    }
  });
}

// ── TOAST ──
function showToast(msg, type = 'success') {
  const container = document.querySelector('.flash-container') || (() => {
    const c = document.createElement('div');
    c.className = 'flash-container';
    document.body.appendChild(c);
    return c;
  })();

  const toast = document.createElement('div');
  toast.className = `flash-msg flash-${type}`;
  toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>${msg}<button onclick="this.parentElement.remove()">×</button>`;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ── MODAL CLOSE ON BG CLICK ──
document.addEventListener('click', (e) => {
  const modal = document.getElementById('loginModal');
  if (modal && e.target === modal) modal.classList.remove('active');
});

// ── SCROLL REVEAL ──
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.product-card, .why-item, .offer-card, .category-box').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});

// ── FILE UPLOAD LABEL ──
document.querySelectorAll('.file-upload-area').forEach(area => {
  const input = area.querySelector('input[type="file"]') || area.nextElementSibling;
  if (!input) return;
  area.addEventListener('click', () => input.click());
  if (input) {
    input.addEventListener('change', () => {
      const p = area.querySelector('p');
      if (p && input.files.length) p.textContent = input.files[0].name;
    });
  }
});

// ── FLOATING NAV ACTIVE ──
const navPills = document.querySelectorAll('.nav-pill');
navPills.forEach(pill => {
  pill.addEventListener('click', () => {
    navPills.forEach(p => p.classList.remove('active'));
    pill.classList.add('active');
  });
});
