document.addEventListener('DOMContentLoaded', () => {
    const loginModal = document.getElementById('login-modal');
    const btnLogin = document.getElementById('btn-login');
    const btnCloseModal = document.getElementById('btn-close-modal');
    const loginForm = document.getElementById('login-form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const btnTogglePassword = document.getElementById('btn-toggle-password');
    const loginError = document.getElementById('login-error');

    // Search elements
    const searchInput = document.getElementById('search-input');
    const searchClear = document.getElementById('search-clear');
    const searchResults = document.getElementById('search-results');
    const searchResultsList = document.getElementById('search-results-list');
    const searchCount = document.getElementById('search-count');
    const searchNoResult = document.getElementById('search-no-result');

    // ─── Build search index from DOM ─────────────────────────────
    const searchIndex = [];

    document.querySelectorAll('.menu-section').forEach(section => {
        const sectionId = section.id;
        // Determine section label & icon
        let sectionLabel = '';
        let sectionIcon = 'bx-food-menu';
        if (sectionId === 'unggulan') { sectionLabel = 'Unggulan'; sectionIcon = 'bxs-crown'; }
        else if (sectionId === 'makanan-berat') { sectionLabel = 'Makanan Berat'; sectionIcon = 'bx-restaurant'; }
        else if (sectionId === 'makanan-ringan') { sectionLabel = 'Makanan Ringan'; sectionIcon = 'bx-croissant'; }
        else if (sectionId === 'minuman') { sectionLabel = 'Minuman'; sectionIcon = 'bx-coffee'; }

        section.querySelectorAll('.product-card').forEach(card => {
            const name = card.querySelector('.product-name')?.textContent.trim() || '';
            const category = card.querySelector('.product-category')?.textContent.trim() || '';
            const price = card.querySelector('.product-price')?.textContent.trim() || '';
            const desc = card.querySelector('.product-desc')?.textContent.trim() || '';

            searchIndex.push({
                name,
                category,
                price,
                description: desc,
                sectionLabel,
                sectionIcon,
                sectionId,
                cardElement: card
            });
        });
    });

    // Open modal
    btnLogin.addEventListener('click', () => {
        loginModal.classList.add('active');
        setTimeout(() => usernameInput.focus(), 100);
    });

    // Close modal
    const closeModal = () => {
        loginModal.classList.remove('active');
        loginForm.reset();
        loginError.style.display = 'none';
        passwordInput.type = 'password';
        btnTogglePassword.innerHTML = "<i class='bx bx-hide'></i>";
    };

    btnCloseModal.addEventListener('click', closeModal);

    // Close modal when clicking outside content
    loginModal.addEventListener('click', (e) => {
        if (e.target === loginModal) {
            closeModal();
        }
    });

    // Toggle password visibility
    btnTogglePassword.addEventListener('click', () => {
        if (passwordInput.type === 'password') {
            passwordInput.type = 'text';
            btnTogglePassword.innerHTML = "<i class='bx bx-show'></i>";
        } else {
            passwordInput.type = 'password';
            btnTogglePassword.innerHTML = "<i class='bx bx-hide'></i>";
        }
    });

    // Handle form submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = usernameInput.value;
        const password = passwordInput.value;
        const submitBtn = loginForm.querySelector('button[type="submit"]');

        if (!username || !password) {
            loginError.textContent = 'Username dan Password tidak boleh kosong.';
            loginError.style.display = 'block';
            return;
        }

        try {
            submitBtn.textContent = 'Memproses...';
            submitBtn.disabled = true;

            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ username, password })
            });

            const data = await response.json();

            if (data.success) {
                // In a real app, redirect or update UI
                loginError.style.display = 'none';
                submitBtn.textContent = 'Berhasil!';
                submitBtn.style.backgroundColor = '#2ecc71';
                setTimeout(() => {
                    closeModal();
                    submitBtn.textContent = 'Masuk ke Sistem';
                    submitBtn.style.backgroundColor = '';
                    submitBtn.disabled = false;
                    window.location.href = '/admin';
                }, 1000);
            } else {
                loginError.textContent = data.message || 'Username atau password salah.';
                loginError.style.display = 'block';
                submitBtn.textContent = 'Masuk ke Sistem';
                submitBtn.disabled = false;
            }
        } catch (error) {
            loginError.textContent = 'Terjadi kesalahan pada server.';
            loginError.style.display = 'block';
            submitBtn.textContent = 'Masuk ke Sistem';
            submitBtn.disabled = false;
        }
    });

    // ─── Search functionality ─────────────────────────────────────
    let searchTimeout;

    // Highlight matching text
    const highlightText = (text, query) => {
        if (!query) return text;
        const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    };

    // Format price for display
    const formatPrice = (price) => {
        return price;
    };

    // Perform search
    const performSearch = (query) => {
        query = query.trim().toLowerCase();

        if (!query) {
            searchResults.classList.remove('active');
            searchClear.style.display = 'none';
            return;
        }

        searchClear.style.display = 'flex';

        // Filter results
        const results = searchIndex.filter(item => {
            return item.name.toLowerCase().includes(query) ||
                item.category.toLowerCase().includes(query) ||
                item.description.toLowerCase().includes(query);
        });

        // Update count
        searchCount.textContent = `${results.length} hasil ditemukan`;

        // Render results
        searchResultsList.innerHTML = '';

        if (results.length === 0) {
            searchNoResult.style.display = 'block';
            searchResultsList.style.display = 'none';
        } else {
            searchNoResult.style.display = 'none';
            searchResultsList.style.display = 'block';

            results.forEach(item => {
                const resultItem = document.createElement('div');
                resultItem.className = 'search-result-item';
                resultItem.innerHTML = `
                    <div class="result-icon">
                        <i class='bx ${item.sectionIcon}'></i>
                    </div>
                    <div class="result-info">
                        <div class="result-name">${highlightText(item.name, query)}</div>
                        <div class="result-meta">
                            <span class="result-category">${item.sectionLabel}</span>
                            <span>·</span>
                            <span>${item.category}</span>
                        </div>
                    </div>
                    <span class="result-price">${item.price}</span>
                `;

                // Click to scroll to product
                resultItem.addEventListener('click', () => {
                    searchResults.classList.remove('active');
                    searchInput.value = '';
                    searchClear.style.display = 'none';

                    // Make sure card is visible
                    item.cardElement.classList.add('card-visible');

                    // Scroll to the card
                    const navHeight = document.querySelector('.navbar').offsetHeight;
                    const targetY = item.cardElement.getBoundingClientRect().top + window.pageYOffset - navHeight - 30;
                    window.scrollTo({ top: targetY, behavior: 'smooth' });

                    // Highlight the card briefly
                    item.cardElement.classList.add('search-highlight');
                    setTimeout(() => {
                        item.cardElement.classList.remove('search-highlight');
                    }, 2000);
                });

                searchResultsList.appendChild(resultItem);
            });
        }

        searchResults.classList.add('active');
    };

    // Search input event with debounce
    searchInput.addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            performSearch(e.target.value);
        }, 200);
    });

    // Show results on focus if there's text
    searchInput.addEventListener('focus', () => {
        if (searchInput.value.trim()) {
            performSearch(searchInput.value);
        }
    });

    // Clear search
    searchClear.addEventListener('click', () => {
        searchInput.value = '';
        searchResults.classList.remove('active');
        searchClear.style.display = 'none';
        searchInput.focus();
    });

    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
        const searchContainer = document.getElementById('search-container');
        if (!searchContainer.contains(e.target)) {
            searchResults.classList.remove('active');
        }
    });

    // Handle Escape key
    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            searchResults.classList.remove('active');
            searchInput.blur();
        }
    });

    // ─── Category cards: smooth scroll to sections ───────────────
    const categoryCards = document.querySelectorAll('.category-card');
    const menuSections = document.querySelectorAll('.menu-section');

    categoryCards.forEach(card => {
        card.addEventListener('click', () => {
            // Update active state
            categoryCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');

            const target = card.dataset.target;

            // Scroll to the targeted section
            const targetSection = document.getElementById(target);
            if (targetSection) {
                const navHeight = document.querySelector('.navbar').offsetHeight;
                const targetY = targetSection.getBoundingClientRect().top + window.pageYOffset - navHeight - 20;
                window.scrollTo({ top: targetY, behavior: 'smooth' });
            }
        });
    });

    // ─── Scroll spy: highlight active category on scroll ─────────
    const observerOptions = {
        root: null,
        rootMargin: '-20% 0px -60% 0px',
        threshold: 0
    };

    const sectionObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const sectionId = entry.target.id;
                categoryCards.forEach(card => {
                    card.classList.remove('active');
                    if (card.dataset.target === sectionId) {
                        card.classList.add('active');
                    }
                });
            }
        });
    }, observerOptions);

    menuSections.forEach(section => {
        sectionObserver.observe(section);
    });

    // ─── Animate product cards on scroll (fade in) ───────────────
    const cardObserverOptions = {
        root: null,
        rootMargin: '0px 0px -50px 0px',
        threshold: 0.1
    };

    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('card-visible');
                cardObserver.unobserve(entry.target);
            }
        });
    }, cardObserverOptions);

    document.querySelectorAll('.product-card').forEach((card, index) => {
        card.style.transitionDelay = `${(index % 3) * 0.1}s`;
        cardObserver.observe(card);
    });

    // ─── Handle heart icon click ─────────────────────────────────
    const heartBtns = document.querySelectorAll('.btn-favorite');
    heartBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            const icon = btn.querySelector('i');
            if (icon.classList.contains('bx-heart')) {
                icon.classList.replace('bx-heart', 'bxs-heart');
                btn.style.color = '#ff4757';
            } else {
                icon.classList.replace('bxs-heart', 'bx-heart');
                btn.style.color = 'var(--primary-color)';
            }
        });
    });

    // ═══════════════════════════════════════════════════════════════
    // Cart Management System
    // ═══════════════════════════════════════════════════════════════
    const cart = [];
    const cartToggle = document.getElementById('cart-toggle');
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartOverlay = document.getElementById('cart-overlay');
    const mobileCartToggle = document.getElementById('mobile-cart-toggle');
    const cartClose = document.getElementById('cart-close');
    const cartCountEl = document.getElementById('cart-count');
    const mobileCartCountEl = document.getElementById('mobile-cart-count');
    const cartBody = document.getElementById('cart-body');
    const cartEmpty = document.getElementById('cart-empty');
    const cartItemsEl = document.getElementById('cart-items');
    const cartForm = document.getElementById('cart-form');
    const cartSummary = document.getElementById('cart-summary');
    const summarySubtotal = document.getElementById('summary-subtotal');
    const summaryTax = document.getElementById('summary-tax');
    const summaryTotal = document.getElementById('summary-total');
    const btnAddMore = document.getElementById('btn-add-more');
    const btnCheckout = document.getElementById('btn-checkout');

    // Format number as Rp price
    const formatRp = (num) => {
        return 'Rp ' + num.toLocaleString('id-ID').replace(/,/g, '.');
    };

    // Open cart sidebar
    const openCart = () => {
        cartSidebar.classList.add('active');
        cartOverlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    };

    // Close cart sidebar
    const closeCart = () => {
        cartSidebar.classList.remove('active');
        cartOverlay.classList.remove('active');
        document.body.style.overflow = '';
    };

    if(cartToggle) cartToggle.addEventListener('click', openCart);
    if(mobileCartToggle) mobileCartToggle.addEventListener('click', openCart);
    if(cartClose) cartClose.addEventListener('click', closeCart);
    if(cartOverlay) cartOverlay.addEventListener('click', closeCart);
    if(btnAddMore) btnAddMore.addEventListener('click', closeCart);

    // ─── Update cart badge count ──────────────────────────────────
    const updateCartCount = () => {
        const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
        if(cartCountEl) cartCountEl.textContent = totalItems;
        if(mobileCartCountEl) mobileCartCountEl.textContent = totalItems;

        // Animate badge
        if(cartCountEl) {
            cartCountEl.style.transform = 'scale(1.4)';
            setTimeout(() => { cartCountEl.style.transform = 'scale(1)'; }, 200);
        }
        if(mobileCartCountEl) {
            mobileCartCountEl.style.transform = 'scale(1.4)';
            setTimeout(() => { mobileCartCountEl.style.transform = 'scale(1)'; }, 200);
        }
    };

    // ─── Update order summary ────────────────────────────────────
    const updateSummary = () => {
        const subtotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
        const tax = Math.round(subtotal * 0.1);
        const total = subtotal + tax;

        summarySubtotal.textContent = formatRp(subtotal);
        summaryTax.textContent = formatRp(tax);
        summaryTotal.textContent = formatRp(total);
    };

    // ─── Sync product card qty stepper with cart ─────────────────
    const syncCardStepper = (productId, qty) => {
        document.querySelectorAll(`.qty-control[data-id="${productId}"]`).forEach(control => {
            const btnBuy = control.querySelector('.btn-buy');
            const stepper = control.querySelector('.qty-stepper');
            const qtyValue = control.querySelector('.qty-value');

            if (qty > 0) {
                btnBuy.style.display = 'none';
                stepper.style.display = 'flex';
                qtyValue.textContent = qty;
            } else {
                btnBuy.style.display = 'flex';
                stepper.style.display = 'none';
                qtyValue.textContent = '1';
            }
        });
    };

    // ─── Render cart items ───────────────────────────────────────
    const renderCart = () => {
        if (cart.length === 0) {
            cartEmpty.style.display = 'block';
            cartItemsEl.style.display = 'none';
            cartForm.style.display = 'none';
            cartSummary.style.display = 'none';
        } else {
            cartEmpty.style.display = 'none';
            cartItemsEl.style.display = 'block';
            cartForm.style.display = 'block';
            cartSummary.style.display = 'block';

            cartItemsEl.innerHTML = '';
            cart.forEach((item, index) => {
                const itemEl = document.createElement('div');
                itemEl.className = 'cart-item';
                itemEl.innerHTML = `
                    <div class="cart-item-header">
                        <span class="cart-item-name">${item.name}</span>
                        <button class="cart-item-delete" data-index="${index}"><i class='bx bx-trash'></i></button>
                    </div>
                    <div class="cart-item-desc">${item.category}</div>
                    <div class="cart-item-footer">
                        <span class="cart-item-unit-price">${formatRp(item.price)}</span>
                        <div class="cart-item-controls">
                            <div class="cart-item-stepper">
                                <button class="qty-btn qty-minus" data-index="${index}"><i class='bx bx-minus'></i></button>
                                <span class="qty-value">${item.qty}</span>
                                <button class="qty-btn qty-plus" data-index="${index}"><i class='bx bx-plus'></i></button>
                            </div>
                            <span class="cart-item-subtotal">${formatRp(item.price * item.qty)}</span>
                        </div>
                    </div>
                `;
                cartItemsEl.appendChild(itemEl);
            });

            // Attach cart item event listeners
            cartItemsEl.querySelectorAll('.cart-item-delete').forEach(btn => {
                btn.addEventListener('click', () => {
                    const idx = parseInt(btn.dataset.index);
                    const removed = cart.splice(idx, 1)[0];
                    syncCardStepper(removed.id, 0);
                    renderCart();
                    updateCartCount();
                    updateSummary();
                });
            });

            cartItemsEl.querySelectorAll('.cart-item-stepper .qty-minus').forEach(btn => {
                btn.addEventListener('click', () => {
                    const idx = parseInt(btn.dataset.index);
                    if (cart[idx].qty > 1) {
                        cart[idx].qty--;
                    } else {
                        const removed = cart.splice(idx, 1)[0];
                        syncCardStepper(removed.id, 0);
                    }
                    renderCart();
                    updateCartCount();
                    updateSummary();
                    // Sync card stepper if item still exists
                    if (cart[idx]) syncCardStepper(cart[idx].id, cart[idx].qty);
                });
            });

            cartItemsEl.querySelectorAll('.cart-item-stepper .qty-plus').forEach(btn => {
                btn.addEventListener('click', () => {
                    const idx = parseInt(btn.dataset.index);
                    if (cart[idx].qty < cart[idx].stock) {
                        cart[idx].qty++;
                        syncCardStepper(cart[idx].id, cart[idx].qty);
                        renderCart();
                        updateCartCount();
                        updateSummary();
                    } else {
                        alert(`Maaf, stok maksimal untuk produk ini adalah ${cart[idx].stock}.`);
                    }
                });
            });
        }

        updateCartCount();
        updateSummary();
    };

    // ─── Add to cart from product card ───────────────────────────
    const addToCart = (id, name, price, category, stock) => {
        const existing = cart.find(item => item.id === id);
        if (existing) {
            if (existing.qty < stock) {
                existing.qty++;
            } else {
                alert(`Maaf, stok maksimal untuk produk ini adalah ${stock}.`);
                return;
            }
        } else {
            if (stock > 0) {
                cart.push({ id, name, price: parseInt(price), category, qty: 1, stock: parseInt(stock) });
            } else {
                alert('Maaf, produk ini sedang habis.');
                return;
            }
        }
        const currentItem = cart.find(item => item.id === id);
        syncCardStepper(id, currentItem.qty);
        renderCart();
    };

    // ─── Product card qty controls ───────────────────────────────
    document.querySelectorAll('.qty-control').forEach(control => {
        const id = control.dataset.id;
        const name = control.dataset.name;
        const price = control.dataset.price;
        const category = control.dataset.category;
        const stock = parseInt(control.dataset.stock) || 0;
        const btnBuy = control.querySelector('.btn-buy');
        const stepper = control.querySelector('.qty-stepper');
        const qtyValue = control.querySelector('.qty-value');
        const minusBtn = control.querySelector('.qty-minus');
        const plusBtn = control.querySelector('.qty-plus');

        if (stock <= 0) {
            btnBuy.innerHTML = 'Habis';
            btnBuy.style.opacity = '0.5';
            btnBuy.style.cursor = 'not-allowed';
            btnBuy.disabled = true;
        }

        // Click "Beli" → add 1 to cart, show stepper
        btnBuy.addEventListener('click', () => {
            if (stock > 0) {
                addToCart(id, name, price, category, stock);
            }
        });

        // Plus on card
        plusBtn.addEventListener('click', () => {
            const item = cart.find(i => i.id === id);
            if (item) {
                if (item.qty < stock) {
                    item.qty++;
                    qtyValue.textContent = item.qty;
                    renderCart();
                } else {
                    alert(`Maaf, stok maksimal untuk produk ini adalah ${stock}.`);
                }
            }
        });

        // Minus on card
        minusBtn.addEventListener('click', () => {
            const item = cart.find(i => i.id === id);
            if (item) {
                item.qty--;
                if (item.qty <= 0) {
                    cart.splice(cart.indexOf(item), 1);
                    btnBuy.style.display = 'flex';
                    stepper.style.display = 'none';
                    qtyValue.textContent = '1';
                } else {
                    qtyValue.textContent = item.qty;
                }
                renderCart();
            }
        });
    });

    // ─── Payment method selection ────────────────────────────────
    document.querySelectorAll('.payment-option').forEach(option => {
        option.addEventListener('click', () => {
            document.querySelectorAll('.payment-option').forEach(o => o.classList.remove('active'));
            option.classList.add('active');
        });
    });

    // ─── Checkout ────────────────────────────────────────────────
    btnCheckout.addEventListener('click', () => {
        if (cart.length === 0) return;

        const meja = document.getElementById('input-meja').value.trim();
        const nama = document.getElementById('input-nama').value.trim();

        if (!meja) {
            alert('Mohon isi nomor meja terlebih dahulu.');
            document.getElementById('input-meja').focus();
            return;
        }
        if (!nama) {
            alert('Mohon isi nama customer terlebih dahulu.');
            document.getElementById('input-nama').focus();
            return;
        }

        const subtotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
        const tax = Math.round(subtotal * 0.1);
        const total = subtotal + tax;
        const method = document.querySelector('.payment-option.active')?.dataset.method || 'tunai';
        const btnOriginalText = btnCheckout.innerHTML;
        btnCheckout.disabled = true;
        btnCheckout.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Memproses...';

        const payload = {
            table_number: meja,
            customer_name: nama,
            payment_method: method,
            items: cart.map(item => ({ id: item.id, qty: item.qty })),
            status: 'Pending'
        };

        fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                if (data.snap_token) {
                    let paymentHandled = false;
                    window.snap.pay(data.snap_token, {
                        onSuccess: function(result) { 
                            paymentHandled = true;
                            fetch('/api/success_order', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ order_id: data.order_id })
                            }).then(() => {
                                alert("✅ Pesanan berhasil diproses!"); 
                                window.location.reload(); 
                            });
                        },
                        onPending: function(result) { 
                            paymentHandled = true;
                            alert("⏳ Pesanan sedang diproses. Mohon tunggu konfirmasi."); 
                            window.location.reload(); 
                        },
                        onError: function(result) { 
                            paymentHandled = true;
                            // Cancel order and restore stock
                            fetch('/api/cancel_order', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ order_id: data.order_id, items: payload.items })
                            });
                            alert("❌ Pembayaran gagal! Silakan coba lagi."); 
                        },
                        onClose: function() { 
                            if (!paymentHandled) {
                                // Cancel order and restore stock
                                fetch('/api/cancel_order', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ order_id: data.order_id, items: payload.items })
                                });
                                alert("⚠️ Anda membatalkan pembayaran. Silakan coba lagi dari keranjang."); 
                            }
                        }
                    });
                } else {
                    if (method === 'tunai') {
                        // Tampilkan modal pending
                        const modal = document.getElementById('pending-payment-modal');
                        if(modal) {
                            modal.classList.add('active');
                            modal.style.display = 'flex';
                        }
                        
                        // Mulai polling status
                        const pollInterval = setInterval(() => {
                            fetch(`/api/order/status/${data.order_id}`)
                            .then(res => res.json())
                            .then(statusData => {
                                if (statusData.success && statusData.status === 'Completed') {
                                    clearInterval(pollInterval);
                                    if(modal) {
                                        document.getElementById('pending-modal-icon').innerHTML = "<i class='bx bx-check-circle' style='font-size: 4rem; color: #16a34a;'></i>";
                                        document.getElementById('pending-modal-title').innerText = "Pembayaran Berhasil!";
                                        document.getElementById('pending-modal-status').innerText = "Status: Completed";
                                        document.getElementById('pending-modal-status').style.color = "#16a34a";
                                        document.getElementById('pending-modal-desc').innerText = `Nama: ${nama} | Meja: ${meja} | Total: ${formatRp(total)}\nPesanan Anda sedang diproses ke dapur.`;
                                        document.getElementById('pending-modal-loader').style.display = "none";
                                        
                                        setTimeout(() => {
                                            window.location.reload();
                                        }, 3500);
                                    } else {
                                        alert(`✅ Pesanan berhasil!\n\nNama: ${nama}\nMeja: ${meja}\nMetode: TUNAI\nTotal: ${formatRp(total)}\n\nPesanan Anda sedang diproses ke dapur.`);
                                        window.location.reload();
                                    }
                                }
                            })
                            .catch(err => console.error("Polling error:", err));
                        }, 2000);
                    } else {
                        alert(`✅ Pesanan berhasil!\n\nNama: ${nama}\nMeja: ${meja}\nMetode: ${method.toUpperCase()}\nTotal: ${formatRp(total)}\n\nPesanan Anda sedang diproses ke dapur.`);
                        window.location.reload();
                    }
                }
            } else {
                alert(`❌ Gagal: ${data.message}`);
            }
        })
        .catch(err => {
            console.error(err);
            alert('Terjadi kesalahan jaringan.');
        })
        .finally(() => {
            btnCheckout.disabled = false;
            btnCheckout.innerHTML = btnOriginalText;
        });
    });
});

