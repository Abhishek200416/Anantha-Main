"""
Seed file for Anantha Lakshmi Traditional Food Products
Based on original handwritten product list
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
DB_NAME = os.environ.get("DB_NAME", "anantha_lakshmi_db")
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]

# All products with authentic names and prices from handwritten list
PRODUCTS = [
    # ==================== POWDERS (PODIS) - 13 Products ====================
    {
        "id": "prod_kandi_podi",
        "name": "Kandi Podi",
        "description": "Traditional lentil powder made from roasted toor dal with spices, perfect for mixing with rice and ghee",
        "category": "powders",
        "image": "https://images.unsplash.com/photo-1716816211590-c15a328a5ff0",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Traditional",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_kakarikaya_karam",
        "name": "Kakarikaya Karam",
        "description": "Spicy bitter gourd powder, healthy and flavorful traditional Andhra preparation",
        "category": "powders",
        "image": "https://images.unsplash.com/photo-1675654871683-abf6524f68c6",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_kobbari_karam",
        "name": "Kobbari Karam",
        "description": "Spicy coconut powder with roasted chilies and spices, excellent with rice",
        "category": "powders",
        "image": "https://images.unsplash.com/photo-1559658166-be35cc5eb9cb",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Spicy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_flax_seeds_powder",
        "name": "Aavachai (Flax Seeds Powder)",
        "description": "Nutritious flax seeds powder, rich in omega-3 and fiber for healthy living",
        "category": "powders",
        "image": "https://images.unsplash.com/photo-1749043998812-0faf9fc714c7",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_mulakada_karapodi",
        "name": "Mulakada Karapodi",
        "description": "Drumstick leaves powder, highly nutritious and traditional Andhra recipe",
        "category": "powders",
        "image": "https://images.pexels.com/photos/2802527/pexels-photo-2802527.jpeg",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_nalla_karam_podi",
        "name": "Nalla Karam Podi",
        "description": "Black pepper powder mix with spices, adds amazing flavor to any dish",
        "category": "powders",
        "image": "https://images.pexels.com/photos/1340116/pexels-photo-1340116.jpeg",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Spicy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_pudina_podi",
        "name": "Pudina Podi",
        "description": "Mint powder with roasted lentils and spices, refreshing and aromatic",
        "category": "powders",
        "image": "https://images.pexels.com/photos/2632292/pexels-photo-2632292.jpeg",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Fresh",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_dhaniya_podi",
        "name": "Dhaniya Podi",
        "description": "Coriander seed powder with spices, essential for South Indian cuisine",
        "category": "powders",
        "image": "https://images.pexels.com/photos/4199098/pexels-photo-4199098.jpeg",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Traditional",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_curry_leaves_podi",
        "name": "Karra Podi (Curry Leaves Powder)",
        "description": "Aromatic curry leaves powder, adds authentic South Indian flavor",
        "category": "powders",
        "image": "https://images.pexels.com/photos/3233275/pexels-photo-3233275.jpeg",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Aromatic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_nuvvula_podi",
        "name": "Nuvvula Podi",
        "description": "Sesame seed powder with spices, rich in calcium and flavor",
        "category": "powders",
        "image": "https://images.pexels.com/photos/1033730/pexels-photo-1033730.jpeg",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Nutritious",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_veerusenaga_podi",
        "name": "Veerusenaga Podi",
        "description": "Peanut powder with red chilies and garlic, protein-rich and delicious",
        "category": "powders",
        "image": "https://images.pexels.com/photos/4397255/pexels-photo-4397255.jpeg",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Protein",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_idly_karapodi",
        "name": "Idly Karapodi",
        "description": "Classic idli chutney powder, essential accompaniment for idli and dosa",
        "category": "powders",
        "image": "https://images.pexels.com/photos/3040873/pexels-photo-3040873.jpeg",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Classic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_sprouted_ragi_powder",
        "name": "Sprouted Ragi Powder",
        "description": "Nutritious sprouted finger millet powder, excellent for health-conscious individuals",
        "category": "powders",
        "image": "https://images.pexels.com/photos/6220707/pexels-photo-6220707.jpeg",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "300g", "price": 300},
            {"weight": "600g", "price": 600}
        ],
        "isBestSeller": False,
        "isNew": True,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    
    # ==================== HOT ITEMS (SNACKS) - 10 Products ====================
    {
        "id": "prod_atukulu_mixture",
        "name": "Atukulu Mixture",
        "description": "Crispy poha mixture with peanuts and spices, perfect tea-time snack",
        "category": "hot-items",
        "image": "https://images.unsplash.com/photo-1589301773859-bb024d3ad558",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "300g", "price": 300},
            {"weight": "600g", "price": 600}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Crispy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_hot_garavaalu",
        "name": "Hot Garavaalu",
        "description": "Spicy deep-fried shell-shaped snack, traditional Andhra delicacy",
        "category": "hot-items",
        "image": "https://images.unsplash.com/photo-1683533678033-f5d60f0a3437",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "300g", "price": 300},
            {"weight": "600g", "price": 600}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Spicy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_hot_kajaalu",
        "name": "Hot Kajaalu",
        "description": "Crispy twisted snack with perfect spice balance, festival favorite",
        "category": "hot-items",
        "image": "https://images.unsplash.com/photo-1613764816537-a43baeb559c1",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "300g", "price": 300},
            {"weight": "600g", "price": 600}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Crispy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_karapusa",
        "name": "Karapusa",
        "description": "Spicy puffed rice snack, light and crunchy with bold flavors",
        "category": "hot-items",
        "image": "https://images.unsplash.com/photo-1631788012442-633d4f91ad31",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "300g", "price": 300},
            {"weight": "600g", "price": 600}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Light",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_ragi_chakkraallu",
        "name": "Ragi Chakkraallu",
        "description": "Healthy ragi (finger millet) murukku, nutritious and delicious",
        "category": "hot-items",
        "image": "https://images.unsplash.com/photo-1631788012420-a0d6a3cfcdfb",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "300g", "price": 300},
            {"weight": "600g", "price": 600}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_ragi_karabundi",
        "name": "Ragi Karabundi",
        "description": "Spicy ragi laddu snack, unique combination of health and taste",
        "category": "hot-items",
        "image": "https://images.unsplash.com/photo-1711565129645-e2fd3e09ff18",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "350g", "price": 350},
            {"weight": "700g", "price": 700}
        ],
        "isBestSeller": False,
        "isNew": True,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_ragi_ribbon_pakodi",
        "name": "Ragi Ribbon Pakodi",
        "description": "Healthy ragi ribbon pakoda, crispy and nutritious snack",
        "category": "hot-items",
        "image": "https://images.unsplash.com/photo-1671981200629-014c03829abb",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_ribbon_pakodi",
        "name": "Ribbon Pakodi",
        "description": "Classic ribbon pakoda, crispy and perfect with evening tea",
        "category": "hot-items",
        "image": "https://images.pexels.com/photos/8489804/pexels-photo-8489804.jpeg",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "300g", "price": 300},
            {"weight": "600g", "price": 600}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Classic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_palli_pakodi",
        "name": "Palli Pakodi",
        "description": "Peanut pakoda, crunchy and protein-rich traditional snack",
        "category": "hot-items",
        "image": "https://images.pexels.com/photos/2302809/pexels-photo-2302809.jpeg",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "320g", "price": 320},
            {"weight": "640g", "price": 640}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Protein",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_kaju_masala",
        "name": "Kaju Masala",
        "description": "Premium spiced cashew nuts, luxury snack for special occasions",
        "category": "hot-items",
        "image": "https://images.pexels.com/photos/8489802/pexels-photo-8489802.jpeg",
        "prices": [
            {"weight": "250g", "price": 350},
            {"weight": "500g", "price": 700},
            {"weight": "1kg", "price": 1400}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Premium",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    
    # ==================== CHIKKIS & SWEETS - 3 Products ====================
    {
        "id": "prod_bhoondi",
        "name": "Bhoondi",
        "description": "Tiny fried gram flour balls, perfect for mixing with curd or as snack",
        "category": "snacks",
        "image": "https://images.unsplash.com/photo-1635952346904-95f2ccfcd029",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "300g", "price": 300},
            {"weight": "600g", "price": 600}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Classic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_masala_chekkalu",
        "name": "Masala Chekkalu",
        "description": "Spiced rice crackers, thin and crispy traditional Andhra snack",
        "category": "snacks",
        "image": "https://images.unsplash.com/photo-1699708263762-00ca477760bd",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Crispy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_ragi_masala_chekkalu",
        "name": "Ragi Masala Chekkalu",
        "description": "Healthy ragi crackers with spices, nutritious version of traditional chekkalu",
        "category": "snacks",
        "image": "https://images.unsplash.com/photo-1695568181747-f54dff1d4654",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "450g", "price": 450},
            {"weight": "900g", "price": 900}
        ],
        "isBestSeller": False,
        "isNew": True,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    
    # ==================== PICKLES - 9 Products ====================
    {
        "id": "prod_tomato_pickle",
        "name": "Tomato Pickle",
        "description": "Tangy tomato pickle with authentic Andhra spices, pairs well with rice and roti",
        "category": "pickles",
        "image": "https://images.unsplash.com/photo-1617854307432-13950e24ba07",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Tangy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_pandu_mirchi_gongura",
        "name": "Pandu Mirchi Gongura Pickle",
        "description": "Green chilli and sorrel leaves pickle, spicy and tangy Andhra specialty",
        "category": "pickles",
        "image": "https://images.unsplash.com/photo-1601702538934-efffab ab67ab65",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Spicy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_allam_pickle",
        "name": "Allam Pickle (Ginger Pickle)",
        "description": "Spicy ginger pickle, aids digestion and adds zing to your meals",
        "category": "pickles",
        "image": "https://images.unsplash.com/photo-1623207485293-fc768c6575fa",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_lemon_pickle",
        "name": "Lemon Pickle",
        "description": "Classic lemon pickle with perfect balance of tangy and spicy flavors",
        "category": "pickles",
        "image": "https://images.pexels.com/photos/12392833/pexels-photo-12392833.jpeg",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Classic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_mango_pickle",
        "name": "Mango Pickle",
        "description": "Traditional raw mango pickle, the king of all pickles in Indian cuisine",
        "category": "pickles",
        "image": "https://images.pexels.com/photos/34159107/pexels-photo-34159107.jpeg",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Classic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_amla_pickle",
        "name": "Amla Pickle (Indian Gooseberry)",
        "description": "Nutritious amla pickle, rich in Vitamin C and traditional medicinal properties",
        "category": "pickles",
        "image": "https://images.unsplash.com/photo-1698557522954-c82d5c2f0e77",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_pandu_mirchi_pickle",
        "name": "Pandu Mirchi Pickle (Green Chilli)",
        "description": "Fiery green chilli pickle for spice lovers, authentic Andhra preparation",
        "category": "pickles",
        "image": "https://images.unsplash.com/photo-1698557048177-a460bb415177",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Spicy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_amla_tokku",
        "name": "Amla Tokku",
        "description": "Sweet and tangy amla preserve, healthy and delicious",
        "category": "pickles",
        "image": "https://images.pexels.com/photos/4198417/pexels-photo-4198417.jpeg",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "300g", "price": 300},
            {"weight": "600g", "price": 600}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Sweet",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_gongura_pickle",
        "name": "Gongura Pickle",
        "description": "Iconic Andhra sorrel leaves pickle, unique tangy flavor loved by all",
        "category": "pickles",
        "image": "https://images.pexels.com/photos/22891875/pexels-photo-22891875.jpeg",
        "prices": [
            {"weight": "200g", "price": 200},
            {"weight": "400g", "price": 400},
            {"weight": "800g", "price": 800}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Signature",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    
    # ==================== SPICES - 4 Products ====================
    {
        "id": "prod_sambar_powder",
        "name": "Sambar Powder",
        "description": "Authentic South Indian sambar powder, perfect blend for delicious sambar",
        "category": "spices",
        "image": "https://images.unsplash.com/photo-1716816211590-c15a328a5ff0",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Essential",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_rasam_powder",
        "name": "Rasam Powder",
        "description": "Traditional rasam powder, aromatic spice mix for authentic rasam",
        "category": "spices",
        "image": "https://images.unsplash.com/photo-1650559347569-09a6bbed5f28",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500},
            {"weight": "1kg", "price": 1000}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Aromatic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_dhaniya_powder",
        "name": "Dhaniya Powder (Coriander Powder)",
        "description": "Pure coriander powder, essential spice for Indian cooking",
        "category": "spices",
        "image": "https://images.pexels.com/photos/4198417/pexels-photo-4198417.jpeg",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Essential",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_pulusu_podi",
        "name": "Pulusu Podi (Tamarind Powder)",
        "description": "Tangy tamarind powder mix, perfect for quick and easy pulusu curry",
        "category": "spices",
        "image": "https://images.pexels.com/photos/22891875/pexels-photo-22891875.jpeg",
        "prices": [
            {"weight": "150g", "price": 150},
            {"weight": "250g", "price": 250},
            {"weight": "500g", "price": 500}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Tangy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    
    # ==================== LADDUS - 6 Products ====================
    {
        "id": "prod_immunity_dry_fruits_laddu",
        "name": "Immunity Dry Fruits Laddu",
        "description": "Premium laddu packed with dry fruits, nuts and immunity-boosting ingredients",
        "category": "laddus",
        "image": "https://images.unsplash.com/photo-1635952346904-95f2ccfcd029",
        "prices": [
            {"weight": "250g", "price": 400},
            {"weight": "1kg", "price": 1500}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Premium",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_ragi_dry_fruits_laddu",
        "name": "Ragi Dry Fruits Laddu",
        "description": "Healthy ragi laddus with dry fruits, perfect combination of nutrition and taste",
        "category": "laddus",
        "image": "https://images.unsplash.com/photo-1610508500445-a4592435e27e",
        "prices": [
            {"weight": "250g", "price": 300},
            {"weight": "1kg", "price": 1200}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_groundnut_laddu",
        "name": "Groundnut Laddu (Palli Undalu)",
        "description": "Traditional groundnut laddus, protein-rich and delicious",
        "category": "laddus",
        "image": "https://images.pexels.com/photos/18488297/pexels-photo-18488297.jpeg",
        "prices": [
            {"weight": "250g", "price": 300},
            {"weight": "1kg", "price": 1100}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Protein",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_oats_laddu",
        "name": "Oats Laddu",
        "description": "Healthy oats laddus, perfect for health-conscious sweet lovers",
        "category": "laddus",
        "image": "https://images.pexels.com/photos/8887200/pexels-photo-8887200.jpeg",
        "prices": [
            {"weight": "250g", "price": 300}
        ],
        "isBestSeller": False,
        "isNew": True,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_kobbari_laddu",
        "name": "Kobbari Laddu (Coconut Laddu)",
        "description": "Classic coconut laddus, sweet and aromatic traditional favorite",
        "category": "laddus",
        "image": "https://images.unsplash.com/photo-1695568180070-8b5acead5cf4",
        "prices": [
            {"weight": "185g", "price": 185},
            {"weight": "680g", "price": 680}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Classic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_nuvvulu_sesame_laddu",
        "name": "Nuvvulu Laddu (Sesame Laddu)",
        "description": "Traditional sesame seed laddus, rich in calcium and delicious flavor",
        "category": "laddus",
        "image": "https://images.pexels.com/photos/8887249/pexels-photo-8887249.jpeg",
        "prices": [
            {"weight": "500g", "price": 400},
            {"weight": "1kg", "price": 800}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Nutritious",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    
    # ==================== CHIKKIS - 4 Products ====================
    {
        "id": "prod_dry_fruits_chikki",
        "name": "Dry Fruits Chikki",
        "description": "Premium chikki loaded with mixed dry fruits and nuts",
        "category": "chikkis",
        "image": "https://images.unsplash.com/photo-1662490880155-700ebafbae4c",
        "prices": [
            {"weight": "250g", "price": 300}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Premium",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_palli_chikki",
        "name": "Palli Chikki (Peanut Chikki)",
        "description": "Traditional peanut chikki, crunchy and sweet",
        "category": "chikkis",
        "image": "https://images.unsplash.com/photo-1662490880176-5d248d9b979a",
        "prices": [
            {"weight": "250g", "price": 170}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Classic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_nuvvulu_chikki",
        "name": "Nuvvulu Chikki (Sesame Chikki)",
        "description": "Sesame seed chikki, healthy and tasty treat",
        "category": "chikkis",
        "image": "https://images.pexels.com/photos/34682283/pexels-photo-34682283.jpeg",
        "prices": [
            {"weight": "250g", "price": 170},
            {"weight": "1kg", "price": 650}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_kaju_chikki",
        "name": "Kaju Chikki (Cashew Chikki)",
        "description": "Premium cashew chikki, luxury sweet treat",
        "category": "chikkis",
        "image": "https://images.pexels.com/photos/34642144/pexels-photo-34642144.jpeg",
        "prices": [
            {"weight": "250g", "price": 300}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Premium",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    
    # ==================== TRADITIONAL SWEETS - 9 Products ====================
    {
        "id": "prod_ariselu",
        "name": "Ariselu",
        "description": "Traditional rice flour sweet, festival special delicacy",
        "category": "sweets",
        "image": "https://images.unsplash.com/photo-1699708263762-00ca477760bd",
        "prices": [
            {"weight": "250g", "price": 320},
            {"weight": "1kg", "price": 640}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Festival",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_kobbari_burelu",
        "name": "Kobbari Burelu (Coconut Balls)",
        "description": "Sweet coconut balls with jaggery, traditional Andhra sweet",
        "category": "sweets",
        "image": "https://images.unsplash.com/photo-1695568181747-f54dff1d4654",
        "prices": [
            {"weight": "500g", "price": 320},
            {"weight": "1kg", "price": 640}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Traditional",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_pottu_minapa_undalu",
        "name": "Pottu Minapa Sunni Undalu",
        "description": "Black gram sweet balls, traditional preparation for special occasions",
        "category": "sweets",
        "image": "https://images.unsplash.com/photo-1645453014906-7f2874408d8d",
        "prices": [
            {"weight": "250g", "price": 250},
            {"weight": "1kg", "price": 875}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Special",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_boondi_chekka",
        "name": "Boondi Chekka",
        "description": "Sweet boondi snack, crispy and sweet combination",
        "category": "sweets",
        "image": "https://images.pexels.com/photos/13220344/pexels-photo-13220344.jpeg",
        "prices": [
            {"weight": "250g", "price": 170},
            {"weight": "500g", "price": 330}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Crispy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_sweet_gavvalu",
        "name": "Sweet Gavvalu",
        "description": "Sweet shell-shaped snack, light and delicious",
        "category": "sweets",
        "image": "https://images.pexels.com/photos/6612658/pexels-photo-6612658.jpeg",
        "prices": [
            {"weight": "250g", "price": 160},
            {"weight": "1kg", "price": 600}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Light",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_sweet_kajjikayalu",
        "name": "Sweet Kajjikayalu",
        "description": "Sweet dumplings with coconut filling, festival favorite",
        "category": "sweets",
        "image": "https://images.unsplash.com/photo-1666190092159-3171cf0fbb12",
        "prices": [
            {"weight": "250g", "price": 170},
            {"weight": "1kg", "price": 640}
        ],
        "isBestSeller": True,
        "isNew": False,
        "tag": "Festival",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_kajji_kaya",
        "name": "Kajji Kaya",
        "description": "Traditional sweet preparation, unique and delicious",
        "category": "sweets",
        "image": "https://images.unsplash.com/photo-1605194000384-439c3ced8d15",
        "prices": [
            {"weight": "500g", "price": 400},
            {"weight": "1kg", "price": 800}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Traditional",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_chalimidi",
        "name": "Chalimidi",
        "description": "Traditional rice sweet with jaggery, authentic village recipe",
        "category": "sweets",
        "image": "https://images.unsplash.com/photo-1650175077733-de1aa6f7e53f",
        "prices": [
            {"weight": "500g", "price": 300},
            {"weight": "1kg", "price": 600}
        ],
        "isBestSeller": False,
        "isNew": False,
        "tag": "Authentic",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    },
    {
        "id": "prod_flax_seeds_laddu",
        "name": "Flax Seeds Laddu",
        "description": "Healthy flax seeds laddus, omega-3 rich nutritious sweet",
        "category": "sweets",
        "image": "https://images.unsplash.com/photo-1641420421863-4b7f0940f287",
        "prices": [
            {"weight": "500g", "price": 400},
            {"weight": "1kg", "price": 800}
        ],
        "isBestSeller": False,
        "isNew": True,
        "tag": "Healthy",
        "inventory_count": 100,
        "out_of_stock": False,
        "discount_active": False
    }
]

async def seed_products():
    """Seed all Anantha Lakshmi traditional products"""
    try:
        # Clear existing products
        print("🗑️  Clearing existing products...")
        delete_result = await db.products.delete_many({})
        print(f"   Deleted {delete_result.deleted_count} existing products")
        
        # Insert new products
        print(f"\n📦 Inserting {len(PRODUCTS)} new products...")
        result = await db.products.insert_many(PRODUCTS)
        print(f"   Successfully inserted {len(result.inserted_ids)} products")
        
        # Print summary by category
        print("\n📊 Products by Category:")
        categories = {}
        for product in PRODUCTS:
            cat = product['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        for category, count in sorted(categories.items()):
            print(f"   - {category.title()}: {count} products")
        
        print(f"\n✅ Total Products: {len(PRODUCTS)}")
        print("✅ Database seeding completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Error seeding products: {str(e)}")
        raise

if __name__ == "__main__":
    print("=" * 70)
    print("🌾 ANANTHA LAKSHMI TRADITIONAL FOOD PRODUCTS SEEDER")
    print("=" * 70)
    asyncio.run(seed_products())
    print("=" * 70)
