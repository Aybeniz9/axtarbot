class Product:
    def __init__(self, id: int, name: str, description: str, price: float, category: str, stock: int):
        self.id = id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.stock = stock

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "category": self.category,
            "stock": self.stock
        }

    def __repr__(self):
        return f"<Product {self.name} ({self.category})>"


class ClothingProduct(Product):
    """Geyim kateqoriyası üçün genişləndirilmiş class — inheritance nümunəsi."""
    def __init__(self, id, name, description, price, category, stock, size_options: list):
        super().__init__(id, name, description, price, category, stock)
        self.size_options = size_options

class CartItem:
    def __init__(self, product_id: str, name: str, price: float, quantity: int = 1):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity

    @property
    def total(self):
        return self.price * self.quantity


class Cart:
    def __init__(self):
        self.items: dict[str, CartItem] = {}

    def add(self, product_id, name, price):
        if product_id in self.items:
            self.items[product_id].quantity += 1
        else:
            self.items[product_id] = CartItem(product_id, name, price)

    def remove(self, product_id):
        if product_id in self.items:
            del self.items[product_id]

    @property
    def total_price(self):
        return sum(item.total for item in self.items.values())

    @property
    def item_count(self):
        return sum(item.quantity for item in self.items.values())