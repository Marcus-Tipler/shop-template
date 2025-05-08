document.addEventListener('DOMContentLoaded', function () {
    const galleryItems = document.querySelectorAll('.mft-product');
    const summaryBox = document.getElementById('item-summary');

    galleryItems.forEach(item => {
        item.addEventListener('mouseenter', function () {
            const itemId = this.getAttribute('data-id');

            // Fetch item details using AJAX
            fetch(`/api/item/${itemId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.error) {
                        console.error(data.error);
                        return;
                    }

                    // Populate the summary box with item details
                    document.getElementById('summary-name').textContent = data.name;
                    document.getElementById('summary-description').textContent = data.description;
                    document.getElementById('summary-price').textContent = `Price: £${data.price}`;
                    document.getElementById('summary-reviews').textContent = `Reviews: ${data.reviews}`;
                    document.getElementById('summary-env-impact').textContent = `Environmental Impact: ${data.env_impact}`;

                    // Position and show the summary box
                    const rect = this.getBoundingClientRect();
                    summaryBox.style.top = `${rect.bottom + window.scrollY}px`;
                    summaryBox.style.left = `${rect.left + window.scrollX}px`;
                    summaryBox.style.display = 'block';
                })
                .catch(error => console.error('Error fetching item details:', error));
        });

        item.addEventListener('mouseleave', function () {
            // Hide the summary box when the mouse leaves the item
            summaryBox.style.display = 'none';
        });
    });
});