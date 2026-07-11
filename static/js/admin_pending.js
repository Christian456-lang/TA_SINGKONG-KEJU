document.addEventListener('DOMContentLoaded', () => {
    // ─── Pending Payments Logic ────────────────────────────────────
    
    function bindProcessPaymentButtons() {
        const btnProcessPayments = document.querySelectorAll('.btn-process-payment');
        
        btnProcessPayments.forEach(btn => {
            btn.removeEventListener('click', handleProcessPayment);
            btn.addEventListener('click', handleProcessPayment);
        });
    }

    function handleProcessPayment(e) {
        const btn = e.currentTarget;
        const orderId = btn.dataset.orderid;
        // Redirect to POS with load_order param
        window.location.href = `/admin/kasir?load_order=${encodeURIComponent(orderId)}`;
    }

    // Initial bind
    bindProcessPaymentButtons();

    // ─── Real-time Auto-Update Logic ────────────────────────────────────
    let lastOrderId = null;
    let pendingCount = null;
    let totalAmount = null;

    function checkPendingUpdates() {
        fetch('/api/pending_updates')
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                if (data.error) return;

                if (lastOrderId === null && pendingCount === null) {
                    // First run: just initialize state
                    lastOrderId = data.last_order_id;
                    pendingCount = data.count;
                    totalAmount = data.total_amount;
                } else if (lastOrderId !== data.last_order_id || pendingCount !== data.count || totalAmount !== data.total_amount) {
                    // Changes detected! Fetch the latest HTML without full page refresh
                    fetch('/admin/pending')
                        .then(res => res.text())
                        .then(html => {
                            const parser = new DOMParser();
                            const doc = parser.parseFromString(html, 'text/html');
                            
                            const newGrid = doc.querySelector('.pending-grid');
                            const currentGrid = document.querySelector('.pending-grid');
                            
                            if (newGrid && currentGrid) {
                                currentGrid.innerHTML = newGrid.innerHTML;
                                bindProcessPaymentButtons(); // Re-bind new buttons
                                
                                // Update count text
                                const countText = document.getElementById('pending-count-text');
                                if (countText) {
                                    countText.textContent = `${data.count} Orders Pending`;
                                }
                            }
                            
                            // Update state
                            lastOrderId = data.last_order_id;
                            pendingCount = data.count;
                            totalAmount = data.total_amount;
                        })
                        .catch(err => console.error('Error fetching new pending HTML:', err));
                }
            })
            .catch(err => console.error('Error checking pending updates:', err));
    }

    // Poll every 5 seconds (optimized for deployment to check lightly)
    setInterval(checkPendingUpdates, 5000);
});
