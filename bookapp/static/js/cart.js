document.addEventListener('DOMContentLoaded', function() {
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();  // Ngừng hành động mặc định của liên kết
            const bookId = this.dataset.id;
            const bookName = this.dataset.name;
            const bookPrice = this.dataset.price;

            // Gửi yêu cầu thêm sản phẩm vào giỏ hàng
            addToCart(bookId, bookName, bookPrice);
        });
    });
});

function addToCart(id, name, price) {
    fetch('/api/add-cart', {
        method: 'POST',
        body: JSON.stringify({
            'id': id,
            'name': name,
            'price': price
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        // Cập nhật số lượng giỏ hàng trên header
        document.getElementById('cartCounter').innerText = data.total_quantity;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function pay(){
    if(confirm('Do you want to pay?')==true){
         fetch('/api/pay', {
            method: 'post'
        }).then(function(res){
            return res.json()
        }).then(function(data){
            if(data.code == 200){
                location.reload()
            }
        }).catch(function(err){
            console.error(err)
        })
    }
}