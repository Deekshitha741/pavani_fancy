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
    const next = html.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    html.setAttribute('data-theme', next);
    localStorage.setItem('sp-theme', next);
    updateThemeIcon(next);
  });
}
function updateThemeIcon(theme) {
  if (themeIcon) themeIcon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
}

// ── MOBILE MENU ──
const hamburger = document.getElementById('hamburger');
const mobileMenu = document.getElementById('mobileMenu');
const closeMenu = document.getElementById('closeMenu');
const overlay = document.getElementById('overlay');
if (hamburger) hamburger.addEventListener('click', () => { mobileMenu.classList.add('open'); overlay.classList.add('active'); document.body.style.overflow = 'hidden'; });
if (closeMenu) closeMenu.addEventListener('click', closeMobileMenu);
if (overlay) overlay.addEventListener('click', closeMobileMenu);
function closeMobileMenu() {
  if (mobileMenu) mobileMenu.classList.remove('open');
  if (overlay) overlay.classList.remove('active');
  document.body.style.overflow = '';
}

// ── ADMIN SIDEBAR MOBILE ──
const adminHamburger = document.getElementById('adminHamburger');
const adminSidebar = document.getElementById('adminSidebar');
const adminOverlay = document.getElementById('adminOverlay');
const adminCloseBtn = document.getElementById('adminCloseBtn');
if (adminHamburger) adminHamburger.addEventListener('click', () => { adminSidebar.classList.add('open'); adminOverlay.classList.add('active'); document.body.style.overflow = 'hidden'; });
if (adminCloseBtn) adminCloseBtn.addEventListener('click', closeAdminSidebar);
if (adminOverlay) adminOverlay.addEventListener('click', closeAdminSidebar);
function closeAdminSidebar() {
  if (adminSidebar) adminSidebar.classList.remove('open');
  if (adminOverlay) adminOverlay.classList.remove('active');
  document.body.style.overflow = '';
}

// ── PARTICLES ──
function createParticles() {
  const c = document.querySelector('.hero-particles');
  if (!c) return;
  for (let i = 0; i < 25; i++) {
    const p = document.createElement('div');
    p.className = 'particle';
    p.style.left = Math.random() * 100 + '%';
    p.style.width = p.style.height = (Math.random() * 3 + 1) + 'px';
    p.style.animationDuration = (Math.random() * 10 + 8) + 's';
    p.style.animationDelay = (Math.random() * 8) + 's';
    c.appendChild(p);
  }
}
createParticles();

// ── LOGIN DETECTION — checks multiple places ──
function isLoggedIn() {
  if (document.body && document.body.dataset.loggedIn === 'true') return true;
  if (document.querySelector('[data-logged-in="true"]')) return true;
  if (document.getElementById('cartBadge')) return true;
  return false;
}

// ── CART STATE ──
const cartState = {}; // productId → { itemId, quantity }

// Initialize from server on page load to restore +/- controls
function initCartState() {
  if (!isLoggedIn()) return;
  fetch('/cart/state', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
    .then(r => r.json())
    .then(data => {
      if (!data.items) return;
      data.items.forEach(item => {
        cartState[item.product_id] = { itemId: item.item_id, quantity: item.quantity };
        restoreCartUI(item.product_id, item.quantity);
      });
    })
    .catch(() => {});
}

function restoreCartUI(productId, quantity) {
  const addBtn = document.getElementById(`add-btn-${productId}`);
  const qtyWrap = document.getElementById(`qty-wrap-${productId}`);
  const qtyDisplay = document.getElementById(`qty-${productId}`);
  if (addBtn && qtyWrap) {
    addBtn.style.display = 'none';
    qtyWrap.style.display = 'flex';
    if (qtyDisplay) qtyDisplay.textContent = quantity;
  }
}

document.addEventListener('DOMContentLoaded', initCartState);

// ── ADD TO CART ──
function addToCart(productId, btn) {
  if (!isLoggedIn()) {
    const modal = document.getElementById('loginModal');
    if (modal) modal.classList.add('active');
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
      cartState[productId] = { itemId: data.item_id, quantity: data.quantity };
      const badge = document.getElementById('cartBadge');
      if (badge) badge.textContent = data.cart_count;
      restoreCartUI(productId, data.quantity);
      showToast('Added to cart! ✦', 'success');
      showCheckoutPrompt(data.cart_count);
    } else {
      showToast(data.message || 'Error adding to cart', 'error');
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-plus"></i> Add';
    }
  })
  .catch(() => {
    showToast('Something went wrong', 'error');
    btn.disabled = false;
    btn.innerHTML = '<i class="fas fa-plus"></i> Add';
  });
}

// ── CHECKOUT PROMPT ──
let _cpTimeout;
function showCheckoutPrompt(cartCount) {
  let el = document.getElementById('checkoutPrompt');
  if (!el) {
    el = document.createElement('div');
    el.id = 'checkoutPrompt';
    document.body.appendChild(el);
  }
  el.innerHTML = `
    <div class="cp-inner">
      <span class="cp-icon">🛍️</span>
      <div class="cp-text">
        <strong>${cartCount} item${cartCount !== 1 ? 's' : ''} in cart</strong>
        <span>Ready to checkout?</span>
      </div>
      <a href="/checkout" class="cp-btn">Checkout <i class="fas fa-arrow-right"></i></a>
      <button class="cp-close" onclick="document.getElementById('checkoutPrompt').classList.remove('cp-visible')">×</button>
    </div>`;
  clearTimeout(_cpTimeout);
  el.classList.add('cp-visible');
  _cpTimeout = setTimeout(() => el.classList.remove('cp-visible'), 6000);
}

// ── CHANGE QTY (product cards) ──
function changeQty(productId, action) {
  const state = cartState[productId];
  if (!state) return;
  fetch(`/cart/update/${state.itemId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' },
    body: `action=${action}`
  })
  .then(r => r.json())
  .then(data => {
    if (!data.success) return;
    if (data.removed) {
      delete cartState[productId];
      const addBtn = document.getElementById(`add-btn-${productId}`);
      const qtyWrap = document.getElementById(`qty-wrap-${productId}`);
      if (addBtn) { addBtn.style.display = 'flex'; addBtn.disabled = false; addBtn.innerHTML = '<i class="fas fa-plus"></i> Add'; }
      if (qtyWrap) qtyWrap.style.display = 'none';
      const badge = document.getElementById('cartBadge');
      if (badge) badge.textContent = Math.max(0, parseInt(badge.textContent || '0') - 1);
    } else {
      cartState[productId].quantity = data.quantity;
      const qtyDisplay = document.getElementById(`qty-${productId}`);
      if (qtyDisplay) qtyDisplay.textContent = data.quantity;
    }
  })
  .catch(() => showToast('Something went wrong', 'error'));
}

// ── UPDATE QTY (profile/cart page) ──
function updateQty(itemId, action, displayEl) {
  fetch(`/cart/update/${itemId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'X-Requested-With': 'XMLHttpRequest' },
    body: `action=${action}`
  })
  .then(r => r.json())
  .then(data => {
    if (!data.success) return;
    if (data.removed) {
      const card = displayEl ? displayEl.closest('.cart-item') : null;
      if (card) card.remove();
      const badge = document.getElementById('cartBadge');
      if (badge) badge.textContent = Math.max(0, parseInt(badge.textContent || '0') - 1);
    } else if (displayEl) {
      displayEl.textContent = data.quantity;
    }
    recalcProfileTotal();
  });
}

function recalcProfileTotal() {
  let total = 0;
  document.querySelectorAll('.cart-item').forEach(item => {
    const priceEl = item.querySelector('.cart-item-price');
    if (!priceEl) return;
    const m = priceEl.textContent.match(/₹([\d,]+)\s*×\s*(\d+)/);
    if (m) total += parseInt(m[1].replace(/,/g, '')) * parseInt(m[2]);
  });
  const totalEl = document.querySelector('.cart-total-value');
  if (totalEl) totalEl.textContent = '₹' + total.toLocaleString('en-IN');
}

// ── TOAST ──
function showToast(msg, type = 'success') {
  let container = document.querySelector('.flash-container');
  if (!container) { container = document.createElement('div'); container.className = 'flash-container'; document.body.appendChild(container); }
  const toast = document.createElement('div');
  toast.className = `flash-msg flash-${type}`;
  toast.innerHTML = `<i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>${msg}<button onclick="this.parentElement.remove()">×</button>`;
  container.appendChild(toast);
  setTimeout(() => { if (toast.parentElement) toast.remove(); }, 3500);
}

// ── MODAL CLOSE ON BG ──
document.addEventListener('click', e => {
  const modal = document.getElementById('loginModal');
  if (modal && e.target === modal) modal.classList.remove('active');
});

// ── SCROLL REVEAL ──
const observer = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { e.target.style.opacity = '1'; e.target.style.transform = 'translateY(0)'; } });
}, { threshold: 0.1 });
document.querySelectorAll('.product-card, .why-item, .offer-card, .category-box').forEach(el => {
  el.style.opacity = '0'; el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity .6s ease, transform .6s ease';
  observer.observe(el);
});

// ── FILE UPLOAD ──
document.querySelectorAll('.file-upload-area').forEach(area => {
  const input = area.nextElementSibling;
  if (!input || input.type !== 'file') return;
  area.addEventListener('click', () => input.click());
  input.addEventListener('change', () => {
    const p = area.querySelector('p');
    if (p && input.files.length) p.textContent = input.files[0].name;
  });
});

// ── FLOATING NAV ──
document.querySelectorAll('.nav-pill').forEach(pill => {
  pill.addEventListener('click', () => { document.querySelectorAll('.nav-pill').forEach(p => p.classList.remove('active')); pill.classList.add('active'); });
});

// ── PAYMENT OPTION SELECT ──
function selectPayment(method, el) {
  document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('selected'));
  el.classList.add('selected');
  const radio = el.querySelector('input[type="radio"]');
  if (radio) radio.checked = true;
  document.querySelectorAll('.payment-details').forEach(d => {
    d.style.display = d.dataset.method === method ? 'block' : 'none';
  });
  // Animate the place order button
  const btn = document.getElementById('placeOrderBtn');
  if (btn) {
    btn.style.transform = 'scale(1.03)';
    setTimeout(() => btn.style.transform = '', 200);
  }
}