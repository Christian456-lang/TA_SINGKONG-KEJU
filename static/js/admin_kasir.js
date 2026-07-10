// admin_kasir.js
document.addEventListener('DOMContentLoaded', () => {
    let cart = [];
    let loadedOrderId = null;
    
    const cartItemsEl = document.getElementById('pos-cart-items');
    const subtotalEl = document.getElementById('pos-subtotal');
    const taxEl = document.getElementById('pos-tax');
    const totalEl = document.getElementById('pos-total');
    const btnCheckout = document.getElementById('btn-checkout');
    const btnClear = document.getElementById('btn-clear-cart');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const productCards = document.querySelectorAll('.pos-product-card');
    
    // Formatting currency
    const formatRp = (number) => {
        return new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 0 }).format(number);
    };

    // Filters & Search
    const searchInput = document.getElementById('pos-search-input');
    
    const applyFilters = () => {
        const activeCategory = document.querySelector('.filter-btn.active').dataset.category;
        const searchQuery = searchInput.value.toLowerCase().trim();

        productCards.forEach(card => {
            const matchesCategory = activeCategory === 'all' || card.dataset.category === activeCategory;
            const matchesSearch = card.dataset.name.toLowerCase().includes(searchQuery);

            if (matchesCategory && matchesSearch) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
    };

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            applyFilters();
        });
    });

    if (searchInput) {
        searchInput.addEventListener('input', applyFilters);
    }

    // Add to Cart
    productCards.forEach(card => {
        card.addEventListener('click', () => {
            if (card.classList.contains('out-of-stock')) return;
            
            const id = parseInt(card.dataset.id);
            const name = card.dataset.name;
            const price = parseInt(card.dataset.price);
            const stock = parseInt(card.dataset.stock);
            
            const existing = cart.find(item => item.id === id);
            if (existing) {
                if (existing.qty < stock) {
                    existing.qty++;
                } else {
                    alert(`Stok maksimal untuk ${name} adalah ${stock}`);
                }
            } else {
                if (stock > 0) {
                    cart.push({ id, name, price, qty: 1, stock });
                }
            }
            renderCart();
        });
    });

    // Render Cart
    const renderCart = () => {
        cartItemsEl.innerHTML = '';
        
        if (cart.length === 0) {
            cartItemsEl.innerHTML = '<div class="empty-cart-msg">Keranjang kosong, silakan pilih menu.</div>';
            btnCheckout.disabled = true;
            updateTotals();
            return;
        }

        btnCheckout.disabled = false;

        cart.forEach((item, index) => {
            const el = document.createElement('div');
            el.className = 'cart-item';
            el.innerHTML = `
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">${formatRp(item.price)}</div>
                </div>
                <div class="cart-item-actions">
                    <div class="qty-control-sm">
                        <button class="qty-minus" data-index="${index}"><i class='bx bx-minus'></i></button>
                        <span>${item.qty}</span>
                        <button class="qty-plus" data-index="${index}"><i class='bx bx-plus'></i></button>
                    </div>
                    <div class="cart-item-subtotal">${formatRp(item.price * item.qty)}</div>
                </div>
            `;
            cartItemsEl.appendChild(el);
        });

        // Bind events for plus/minus
        document.querySelectorAll('.qty-minus').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const idx = parseInt(btn.dataset.index);
                if (cart[idx].qty > 1) {
                    cart[idx].qty--;
                } else {
                    cart.splice(idx, 1);
                }
                renderCart();
            });
        });

        document.querySelectorAll('.qty-plus').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const idx = parseInt(btn.dataset.index);
                if (cart[idx].qty < cart[idx].stock) {
                    cart[idx].qty++;
                    renderCart();
                } else {
                    alert(`Stok maksimal: ${cart[idx].stock}`);
                }
            });
        });

        updateTotals();
    };

    const updateTotals = () => {
        const subtotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);
        const tax = Math.round(subtotal * 0.1);
        const total = subtotal + tax;

        subtotalEl.textContent = formatRp(subtotal);
        taxEl.textContent = formatRp(tax);
        totalEl.textContent = formatRp(total);
    };

    btnClear.addEventListener('click', () => {
        if(confirm('Kosongkan keranjang?')) {
            cart = [];
            renderCart();
        }
    });

    // Payment Methods
    document.querySelectorAll('.pay-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.pay-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Checkout
    btnCheckout.addEventListener('click', () => {
        const tableNumber = document.getElementById('pos-table').value.trim();
        const customerName = document.getElementById('pos-customer').value.trim();
        const paymentMethod = document.querySelector('.pay-btn.active').dataset.method;
        
        // Table number is now optional
        // if (!tableNumber) {
        //     alert('Mohon isi nomor meja kustomer!');
        //     document.getElementById('pos-table').focus();
        //     return;
        // }
        if (!customerName && !loadedOrderId) {
            alert('Mohon isi nama kustomer!');
            document.getElementById('pos-customer').focus();
            return;
        }

        btnCheckout.disabled = true;
        btnCheckout.innerHTML = '<i class="bx bx-loader-alt bx-spin"></i> Memproses...';

        const payload = {
            table_number: tableNumber,
            customer_name: customerName,
            payment_method: paymentMethod,
            items: cart.map(item => ({ id: item.id, qty: item.qty }))
        };
        
        if(loadedOrderId) {
            payload.order_id = loadedOrderId;
        }

        fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(response => response.json())
        .then(data => {
            if(data.success) {
                alert(`✅ Pesanan Berhasil Diproses!\nOrder ID: ${data.order_id}`);
                    
                    // Update stock di DOM
                    cart.forEach(item => {
                        const card = Array.from(productCards).find(c => parseInt(c.dataset.id) === item.id);
                        if (card) {
                            let newStock = parseInt(card.dataset.stock) - item.qty;
                            card.dataset.stock = newStock;
                            
                            const badge = card.querySelector('.stock-badge');
                            if (newStock <= 0) {
                                card.classList.add('out-of-stock');
                                if (badge) badge.remove();
                                if (!card.querySelector('.out-of-stock-overlay')) {
                                    const overlay = document.createElement('div');
                                    overlay.className = 'out-of-stock-overlay';
                                    overlay.textContent = 'HABIS';
                                    card.querySelector('.pos-product-img').appendChild(overlay);
                                }
                            } else {
                                if (badge) badge.textContent = newStock;
                            }
                        }
                    });

                    // Kosongkan keranjang & reset form
                    cart = [];
                    loadedOrderId = null;
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
                                alert("Pembayaran berhasil!"); 
                                window.location.href = '/admin/kasir'; 
                            });
                        },
                        onPending: function(result) { 
                            paymentHandled = true;
                            alert("Pembayaran diproses (pending)."); 
                            window.location.href = '/admin/kasir'; 
                        },
                        onError: function(result) { 
                            paymentHandled = true;
                            fetch('/api/cancel_order', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ order_id: data.order_id, items: payload.items })
                            });
                            alert("Pembayaran gagal! Transaksi dibatalkan."); 
                            btnCheckout.disabled = false;
                            btnCheckout.innerHTML = "<i class='bx bx-check-circle'></i> Proses Pesanan";
                        },
                        onClose: function() { 
                            if (!paymentHandled) {
                                fetch('/api/cancel_order', {
                                    method: 'POST',
                                    headers: { 'Content-Type': 'application/json' },
                                    body: JSON.stringify({ order_id: data.order_id, items: payload.items })
                                });
                                alert("Pembayaran ditutup sebelum selesai. Transaksi dibatalkan."); 
                                btnCheckout.disabled = false;
                                btnCheckout.innerHTML = "<i class='bx bx-check-circle'></i> Proses Pesanan";
                            }
                        }
                    });
                } else {
                    alert("Pesanan berhasil diproses!");
                    window.location.href = '/admin/kasir';
                }
            } else {
                alert(`❌ Gagal: ${data.message}`);
                btnCheckout.disabled = false;
                btnCheckout.innerHTML = "<i class='bx bx-check-circle'></i> Proses Pesanan";
            }
        })
        .catch(err => {
            console.error(err);
            alert('Terjadi kesalahan jaringan.');
            btnCheckout.disabled = false;
            btnCheckout.innerHTML = "<i class='bx bx-check-circle'></i> Proses Pesanan";
        });
    });

    // Load Order from URL
    const urlParams = new URLSearchParams(window.location.search);
    const orderIdToLoad = urlParams.get('load_order');
    if (orderIdToLoad) {
        fetch(`/api/orders/${encodeURIComponent(orderIdToLoad)}`)
            .then(res => res.json())
            .then(data => {
                if (data.success && data.order) {
                    loadedOrderId = data.order.order_id;
                    document.getElementById('pos-table').value = data.order.table_number;
                    // Note: customer_name is not saved in Order right now so we leave it empty
                    
                    data.order.items.forEach(item => {
                        cart.push({
                            id: item.id,
                            name: item.name,
                            price: item.price,
                            qty: item.qty,
                            stock: item.stock
                        });
                    });
                    renderCart();
                    
                    // Change button text
                    btnCheckout.innerHTML = `<i class='bx bx-check-circle'></i> Selesaikan Pending (${loadedOrderId})`;
                }
            })
            .catch(err => console.error("Gagal meload order:", err));
    }
});
