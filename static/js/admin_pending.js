document.addEventListener('DOMContentLoaded', () => {
    // ─── Pending Payments Logic ────────────────────────────────────
    const btnProcessPayments = document.querySelectorAll('.btn-process-payment');
    
    btnProcessPayments.forEach(btn => {
        btn.addEventListener('click', function() {
            const orderId = this.dataset.orderid;
            
            // Redirect to POS with load_order param
            window.location.href = `/admin/kasir?load_order=${encodeURIComponent(orderId)}`;
        });
    });
});
