#!/usr/bin/env python3
"""
Script to import products from mock.js into MongoDB database
"""
import asyncio
import os
import sys
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment
load_dotenv(Path(__file__).parent / '.env')

# Products data from mock.js
PRODUCTS = [
  # Laddus & Chikkis (8 items)
  {
    "name": 'Immunity Dry Fruits Laddu',
    "category": 'laddus-chikkis',
    "description": 'Boost immunity with dry fruits',
    "image": 'https://images.unsplash.com/photo-1635952346904-95f2ccfcd029?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 399 },
      { "weight": '1kg', "price": 1499 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Healthy Choice'
  },
  {
    "name": 'Ragi Dry Fruits Laddu',
    "category": 'laddus-chikkis',
    "description": 'Healthy ragi with dry fruits',
    "image": 'https://images.unsplash.com/photo-1605194000384-439c3ced8d15?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 299 },
      { "weight": '1kg', "price": 1199 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Nutritious'
  },
  {
    "name": 'Ground Nut Laddu',
    "category": 'laddus-chikkis',
    "description": 'Traditional groundnut laddu',
    "image": 'https://images.unsplash.com/photo-1610508500445-a4592435e27e?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 150 },
      { "weight": '½ kg', "price": 280 },
      { "weight": '1kg', "price": 550 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Traditional'
  },
  {
    "name": 'Palli Chikki',
    "category": 'laddus-chikkis',
    "description": 'Crunchy peanut chikki',
    "image": 'https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 120 },
      { "weight": '½ kg', "price": 230 },
      { "weight": '1kg', "price": 450 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Crunchy'
  },
  {
    "name": 'Nuvvula Laddu',
    "category": 'laddus-chikkis',
    "description": 'Sesame seed laddu',
    "image": 'https://images.unsplash.com/photo-1599599810769-bcde5a160d32?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 180 },
      { "weight": '½ kg', "price": 350 },
      { "weight": '1kg', "price": 680 }
    ],
    "isBestSeller": False,
    "isNew": True,
    "tag": 'Nutritious'
  },
  {
    "name": 'Til Laddu',
    "category": 'laddus-chikkis',
    "description": 'Traditional til laddu',
    "image": 'https://images.unsplash.com/photo-1635952346904-95f2ccfcd029?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 170 },
      { "weight": '½ kg', "price": 330 },
      { "weight": '1kg', "price": 650 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Traditional'
  },
  {
    "name": 'Copra Laddu',
    "category": 'laddus-chikkis',
    "description": 'Coconut copra laddu',
    "image": 'https://images.unsplash.com/photo-1610508500445-a4592435e27e?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 190 },
      { "weight": '½ kg', "price": 370 },
      { "weight": '1kg', "price": 730 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Traditional'
  },
  {
    "name": 'Dry Fruit Laddu',
    "category": 'laddus-chikkis',
    "description": 'Premium dry fruit laddu',
    "image": 'https://images.unsplash.com/photo-1635952346904-95f2ccfcd029?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 350 },
      { "weight": '½ kg', "price": 680 },
      { "weight": '1kg', "price": 1320 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Premium'
  },
  # Sweets (10 items)
  {
    "name": 'Kaju Katli',
    "category": 'sweets',
    "description": 'Premium cashew sweet',
    "image": 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 450 },
      { "weight": '½ kg', "price": 880 },
      { "weight": '1kg', "price": 1750 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Premium'
  },
  {
    "name": 'Mysore Pak',
    "category": 'sweets',
    "description": 'Traditional Mysore pak',
    "image": 'https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 280 },
      { "weight": '½ kg', "price": 550 },
      { "weight": '1kg', "price": 1080 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Traditional'
  },
  {
    "name": 'Badam Halwa',
    "category": 'sweets',
    "description": 'Rich almond halwa',
    "image": 'https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 420 },
      { "weight": '½ kg', "price": 820 },
      { "weight": '1kg', "price": 1620 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Premium'
  },
  {
    "name": 'Boondi Laddu',
    "category": 'sweets',
    "description": 'Sweet boondi laddu',
    "image": 'https://images.unsplash.com/photo-1635952346904-95f2ccfcd029?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 160 },
      { "weight": '½ kg', "price": 310 },
      { "weight": '1kg', "price": 600 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Traditional'
  },
  {
    "name": 'Rava Laddu',
    "category": 'sweets',
    "description": 'Semolina laddu',
    "image": 'https://images.unsplash.com/photo-1610508500445-a4592435e27e?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 140 },
      { "weight": '½ kg', "price": 270 },
      { "weight": '1kg', "price": 520 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Traditional'
  },
  {
    "name": 'Motichoor Laddu',
    "category": 'sweets',
    "description": 'Fine boondi laddu',
    "image": 'https://images.unsplash.com/photo-1635952346904-95f2ccfcd029?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 180 },
      { "weight": '½ kg', "price": 350 },
      { "weight": '1kg', "price": 680 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Traditional'
  },
  {
    "name": 'Coconut Burfi',
    "category": 'sweets',
    "description": 'Coconut sweet burfi',
    "image": 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 200 },
      { "weight": '½ kg', "price": 390 },
      { "weight": '1kg', "price": 760 }
    ],
    "isBestSeller": False,
    "isNew": True,
    "tag": 'Traditional'
  },
  {
    "name": 'Milk Cake',
    "category": 'sweets',
    "description": 'Soft milk cake',
    "image": 'https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 240 },
      { "weight": '½ kg', "price": 470 },
      { "weight": '1kg', "price": 920 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Traditional'
  },
  {
    "name": 'Gulab Jamun',
    "category": 'sweets',
    "description": 'Classic gulab jamun',
    "image": 'https://images.unsplash.com/photo-1631452180519-c014fe946bc7?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 160 },
      { "weight": '½ kg', "price": 310 },
      { "weight": '1kg', "price": 600 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Traditional'
  },
  {
    "name": 'Jalebi',
    "category": 'sweets',
    "description": 'Crispy jalebi',
    "image": 'https://images.unsplash.com/photo-1609501676725-7186f017a4b7?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 150 },
      { "weight": '½ kg', "price": 290 },
      { "weight": '1kg', "price": 560 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Traditional'
  },
  # Hot Items (8 items)
  {
    "name": 'Samosa',
    "category": 'hot-items',
    "description": 'Crispy vegetable samosa',
    "image": 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500',
    "prices": [
      { "weight": '2 pcs', "price": 40 },
      { "weight": '4 pcs', "price": 75 },
      { "weight": '6 pcs', "price": 110 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Hot & Fresh'
  },
  {
    "name": 'Onion Pakoda',
    "category": 'hot-items',
    "description": 'Crispy onion fritters',
    "image": 'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 80 },
      { "weight": '½ kg', "price": 150 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Hot & Fresh'
  },
  {
    "name": 'Mirchi Bajji',
    "category": 'hot-items',
    "description": 'Spicy chili fritters',
    "image": 'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=500',
    "prices": [
      { "weight": '4 pcs', "price": 60 },
      { "weight": '8 pcs', "price": 115 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Hot & Fresh'
  },
  {
    "name": 'Punugulu',
    "category": 'hot-items',
    "description": 'Idli batter fritters',
    "image": 'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 70 },
      { "weight": '½ kg', "price": 130 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Hot & Fresh'
  },
  {
    "name": 'Bonda',
    "category": 'hot-items',
    "description": 'Potato filled bonda',
    "image": 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500',
    "prices": [
      { "weight": '4 pcs', "price": 60 },
      { "weight": '8 pcs', "price": 115 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Hot & Fresh'
  },
  {
    "name": 'Vada',
    "category": 'hot-items',
    "description": 'Crispy medu vada',
    "image": 'https://images.unsplash.com/photo-1606491956689-2ea866880c84?w=500',
    "prices": [
      { "weight": '4 pcs', "price": 70 },
      { "weight": '8 pcs', "price": 130 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Hot & Fresh'
  },
  {
    "name": 'Mysore Bonda',
    "category": 'hot-items',
    "description": 'Sweet mysore bonda',
    "image": 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500',
    "prices": [
      { "weight": '4 pcs', "price": 60 },
      { "weight": '8 pcs', "price": 115 }
    ],
    "isBestSeller": False,
    "isNew": True,
    "tag": 'Hot & Fresh'
  },
  {
    "name": 'Aloo Bonda',
    "category": 'hot-items',
    "description": 'Potato bonda',
    "image": 'https://images.unsplash.com/photo-1601050690597-df0568f70950?w=500',
    "prices": [
      { "weight": '4 pcs', "price": 65 },
      { "weight": '8 pcs', "price": 120 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Hot & Fresh'
  },
  # Snacks (10 items)
  {
    "name": 'Murukku',
    "category": 'snacks',
    "description": 'Traditional rice murukku',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 100 },
      { "weight": '½ kg', "price": 190 },
      { "weight": '1kg', "price": 370 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Crunchy'
  },
  {
    "name": 'Mixture',
    "category": 'snacks',
    "description": 'Spicy mixture',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 90 },
      { "weight": '½ kg', "price": 170 },
      { "weight": '1kg', "price": 330 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Crunchy'
  },
  {
    "name": 'Boondi',
    "category": 'snacks',
    "description": 'Crispy boondi',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 80 },
      { "weight": '½ kg', "price": 150 },
      { "weight": '1kg', "price": 290 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Crunchy'
  },
  {
    "name": 'Karapusa',
    "category": 'snacks',
    "description": 'Spicy puffed snack',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 85 },
      { "weight": '½ kg', "price": 160 },
      { "weight": '1kg', "price": 310 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Crunchy'
  },
  {
    "name": 'Ribbon Pakoda',
    "category": 'snacks',
    "description": 'Crispy ribbon pakoda',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 95 },
      { "weight": '½ kg', "price": 180 },
      { "weight": '1kg', "price": 350 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Crunchy'
  },
  {
    "name": 'Sev',
    "category": 'snacks',
    "description": 'Fine sev',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 85 },
      { "weight": '½ kg', "price": 160 },
      { "weight": '1kg', "price": 310 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Crunchy'
  },
  {
    "name": 'Chakli',
    "category": 'snacks',
    "description": 'Spiral chakli',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 100 },
      { "weight": '½ kg', "price": 190 },
      { "weight": '1kg', "price": 370 }
    ],
    "isBestSeller": False,
    "isNew": True,
    "tag": 'Crunchy'
  },
  {
    "name": 'Karam Kaju',
    "category": 'snacks',
    "description": 'Spicy cashew snack',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 380 },
      { "weight": '½ kg', "price": 750 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Premium'
  },
  {
    "name": 'Namkeen',
    "category": 'snacks',
    "description": 'Mixed namkeen',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 90 },
      { "weight": '½ kg', "price": 170 },
      { "weight": '1kg', "price": 330 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Crunchy'
  },
  {
    "name": 'Bhujia',
    "category": 'snacks',
    "description": 'Fine bhujia sev',
    "image": 'https://images.unsplash.com/photo-1599490659213-e2b9527bd087?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 95 },
      { "weight": '½ kg', "price": 180 },
      { "weight": '1kg', "price": 350 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Crunchy'
  },
  # Pickles (8 items)
  {
    "name": 'Mango Pickle',
    "category": 'pickles',
    "description": 'Spicy mango pickle',
    "image": 'https://images.unsplash.com/photo-1583623733237-4d5764e9c3f3?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 120 },
      { "weight": '½ kg', "price": 230 },
      { "weight": '1kg', "price": 450 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Tangy'
  },
  {
    "name": 'Lemon Pickle',
    "category": 'pickles',
    "description": 'Tangy lemon pickle',
    "image": 'https://images.unsplash.com/photo-1583623733237-4d5764e9c3f3?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 110 },
      { "weight": '½ kg', "price": 210 },
      { "weight": '1kg', "price": 410 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Tangy'
  },
  {
    "name": 'Gongura Pickle',
    "category": 'pickles',
    "description": 'Andhra gongura pickle',
    "image": 'https://images.unsplash.com/photo-1583623733237-4d5764e9c3f3?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 140 },
      { "weight": '½ kg', "price": 270 },
      { "weight": '1kg', "price": 530 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Special'
  },
  {
    "name": 'Tomato Pickle',
    "category": 'pickles',
    "description": 'Spicy tomato pickle',
    "image": 'https://images.unsplash.com/photo-1583623733237-4d5764e9c3f3?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 100 },
      { "weight": '½ kg', "price": 190 },
      { "weight": '1kg', "price": 370 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Tangy'
  },
  {
    "name": 'Chilli Pickle',
    "category": 'pickles',
    "description": 'Hot chilli pickle',
    "image": 'https://images.unsplash.com/photo-1583623733237-4d5764e9c3f3?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 130 },
      { "weight": '½ kg', "price": 250 },
      { "weight": '1kg', "price": 490 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Hot'
  },
  {
    "name": 'Mixed Pickle',
    "category": 'pickles',
    "description": 'Mixed vegetable pickle',
    "image": 'https://images.unsplash.com/photo-1583623733237-4d5764e9c3f3?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 115 },
      { "weight": '½ kg', "price": 220 },
      { "weight": '1kg', "price": 430 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Tangy'
  },
  {
    "name": 'Garlic Pickle',
    "category": 'pickles',
    "description": 'Spicy garlic pickle',
    "image": 'https://images.unsplash.com/photo-1583623733237-4d5764e9c3f3?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 125 },
      { "weight": '½ kg', "price": 240 },
      { "weight": '1kg', "price": 470 }
    ],
    "isBestSeller": False,
    "isNew": True,
    "tag": 'Spicy'
  },
  {
    "name": 'Amla Pickle',
    "category": 'pickles',
    "description": 'Healthy amla pickle',
    "image": 'https://images.unsplash.com/photo-1583623733237-4d5764e9c3f3?w=500',
    "prices": [
      { "weight": '¼ kg', "price": 135 },
      { "weight": '½ kg', "price": 260 },
      { "weight": '1kg', "price": 510 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Healthy'
  },
  # Powders (8 items)
  {
    "name": 'Sambar Powder',
    "category": 'powders',
    "description": 'Authentic sambar powder',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 60 },
      { "weight": '250g', "price": 140 },
      { "weight": '500g', "price": 270 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Essential'
  },
  {
    "name": 'Rasam Powder',
    "category": 'powders',
    "description": 'Tangy rasam powder',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 55 },
      { "weight": '250g', "price": 130 },
      { "weight": '500g', "price": 250 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Essential'
  },
  {
    "name": 'Curry Powder',
    "category": 'powders',
    "description": 'Aromatic curry powder',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 50 },
      { "weight": '250g', "price": 120 },
      { "weight": '500g', "price": 230 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Essential'
  },
  {
    "name": 'Biryani Masala',
    "category": 'powders',
    "description": 'Special biryani masala',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 70 },
      { "weight": '250g', "price": 165 },
      { "weight": '500g', "price": 320 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Special'
  },
  {
    "name": 'Garam Masala',
    "category": 'powders',
    "description": 'Aromatic garam masala',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 65 },
      { "weight": '250g', "price": 155 },
      { "weight": '500g', "price": 300 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Essential'
  },
  {
    "name": 'Coriander Powder',
    "category": 'powders',
    "description": 'Pure coriander powder',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 40 },
      { "weight": '250g', "price": 95 },
      { "weight": '500g', "price": 180 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Essential'
  },
  {
    "name": 'Turmeric Powder',
    "category": 'powders',
    "description": 'Pure turmeric powder',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 45 },
      { "weight": '250g', "price": 105 },
      { "weight": '500g', "price": 200 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Essential'
  },
  {
    "name": 'Chilli Powder',
    "category": 'powders',
    "description": 'Red chilli powder',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 50 },
      { "weight": '250g', "price": 120 },
      { "weight": '500g', "price": 230 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Essential'
  },
  # Spices (6 items)
  {
    "name": 'Cumin Seeds',
    "category": 'spices',
    "description": 'Premium cumin seeds',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 80 },
      { "weight": '250g', "price": 190 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Essential'
  },
  {
    "name": 'Black Pepper',
    "category": 'spices',
    "description": 'Whole black pepper',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '100g', "price": 120 },
      { "weight": '250g', "price": 290 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Premium'
  },
  {
    "name": 'Cardamom',
    "category": 'spices',
    "description": 'Green cardamom pods',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '50g', "price": 250 },
      { "weight": '100g', "price": 490 }
    ],
    "isBestSeller": True,
    "isNew": False,
    "tag": 'Premium'
  },
  {
    "name": 'Cinnamon Sticks',
    "category": 'spices',
    "description": 'Ceylon cinnamon',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '50g', "price": 90 },
      { "weight": '100g', "price": 170 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Aromatic'
  },
  {
    "name": 'Cloves',
    "category": 'spices',
    "description": 'Whole cloves',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '50g', "price": 110 },
      { "weight": '100g', "price": 210 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Aromatic'
  },
  {
    "name": 'Bay Leaves',
    "category": 'spices',
    "description": 'Dried bay leaves',
    "image": 'https://images.unsplash.com/photo-1596040033229-a0b4b53a1c3d?w=500',
    "prices": [
      { "weight": '50g', "price": 70 },
      { "weight": '100g', "price": 130 }
    ],
    "isBestSeller": False,
    "isNew": False,
    "tag": 'Aromatic'
  }
]


async def import_products():
    """Import all products into MongoDB"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        db_name = os.environ.get('DB_NAME', 'anantha_lakshmi_db')
        
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        
        print(f"Connected to MongoDB: {db_name}")
        
        # Clear existing products (optional - comment out if you want to keep existing)
        # await db.products.delete_many({})
        # print("Cleared existing products")
        
        # Import products with proper IDs
        import time
        imported_count = 0
        
        for i, product in enumerate(PRODUCTS):
            # Generate proper product ID
            product['id'] = f"product_{int(time.time() * 1000) + i}"
            
            # Add default fields
            product['out_of_stock'] = False
            product['inventory_count'] = None
            
            # Insert product
            await db.products.insert_one(product)
            imported_count += 1
            print(f"Imported: {product['name']} (ID: {product['id']})")
        
        print(f"\n✅ Successfully imported {imported_count} products!")
        
        # Show statistics
        total = await db.products.count_documents({})
        print(f"Total products in database: {total}")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error importing products: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(import_products())
