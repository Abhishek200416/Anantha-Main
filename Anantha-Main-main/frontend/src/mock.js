// Complete Mock data for Anantha Lakshmi products

export const categories = [
  { id: 'all', name: 'All' },
  { id: 'laddus-chikkis', name: 'Laddus & Chikkis' },
  { id: 'sweets', name: 'Sweets' },
  { id: 'hot-items', name: 'Hot Items' },
  { id: 'snacks', name: 'Snacks' },
  { id: 'pickles', name: 'Veg Pickles' },
  { id: 'powders', name: 'Powders' },
  { id: 'spices', name: 'Spices' },
  { id: 'other', name: 'Other' },
];

export const products = [
  // Laddus & Chikkis (8 items)
  {
    id: 1,
    name: 'Immunity Dry Fruits Laddu',
    category: 'laddus-chikkis',
    description: 'Boost immunity with dry fruits',
    image: 'https://images.unsplash.com/photo-1635952346904-95f2ccfcd029?w=500',
    prices: [
      { weight: '¼ kg', price: 399 },
      { weight: '1kg', price: 1499 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Healthy Choice'
  },
  {
    id: 2,
    name: 'Ragi Dry Fruits Laddu',
    category: 'laddus-chikkis',
    description: 'Healthy ragi with dry fruits',
    image: 'https://images.unsplash.com/photo-1605194000384-439c3ced8d15?w=500',
    prices: [
      { weight: '¼ kg', price: 299 },
      { weight: '1kg', price: 1199 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Nutritious'
  },
  {
    id: 3,
    name: 'Ground Nut Laddu',
    category: 'laddus-chikkis',
    description: 'Traditional groundnut laddu',
    image: 'https://images.unsplash.com/photo-1610508500445-a4592435e27e?w=500',
    prices: [
      { weight: '¼ kg', price: 299 },
      { weight: '1kg', price: 1099 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Classic Taste'
  },
  {
    id: 4,
    name: 'Oats Laddu',
    category: 'laddus-chikkis',
    description: 'Healthy oats laddu',
    image: 'https://images.unsplash.com/photo-1699708263762-00ca477760bd?w=500',
    prices: [
      { weight: '¼ kg', price: 299 }
    ],
    isBestSeller: false,
    isNew: true,
    tag: 'New Arrival'
  },
  {
    id: 5,
    name: 'Dry Fruits Chikki',
    category: 'laddus-chikkis',
    description: 'Crunchy dry fruits chikki',
    image: 'https://images.unsplash.com/photo-1695568181747-f54dff1d4654?w=500',
    prices: [
      { weight: '¼ kg', price: 299 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Crispy Delight'
  },
  {
    id: 6,
    name: 'Palli Chikki',
    category: 'laddus-chikkis',
    description: 'Groundnut chikki',
    image: 'https://images.unsplash.com/photo-1695568180070-8b5acead5cf4?w=500',
    prices: [
      { weight: '¼ kg', price: 169 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Best Value'
  },
  {
    id: 7,
    name: 'Nuvvulu Chikki',
    category: 'laddus-chikkis',
    description: 'Sesame chikki',
    image: 'https://images.pexels.com/photos/3026811/pexels-photo-3026811.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 169 },
      { weight: '1kg', price: 649 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Traditional'
  },
  {
    id: 8,
    name: 'Kaju Chikki',
    category: 'laddus-chikkis',
    description: 'Premium cashew chikki',
    image: 'https://images.unsplash.com/photo-1662490880176-5d248d9b979a?w=500',
    prices: [
      { weight: '¼ kg', price: 299 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Premium Quality'
  },

  // Sweets (10 items)
  {
    id: 9,
    name: 'Kobbari Laddu',
    category: 'sweets',
    description: 'Coconut laddu',
    image: 'https://images.unsplash.com/photo-1727018427695-35a6048c91e7?w=500',
    prices: [
      { weight: '½ kg', price: 399 },
      { weight: '1kg', price: 699 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Festival Special'
  },
  {
    id: 10,
    name: 'Ariselu',
    category: 'sweets',
    description: 'Traditional rice sweet',
    image: 'https://images.unsplash.com/photo-1727018792817-2dae98db2294?w=500',
    prices: [
      { weight: '½ kg', price: 319 },
      { weight: '1kg', price: 639 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Authentic Recipe'
  },
  {
    id: 11,
    name: 'Kobbari Burellu',
    category: 'sweets',
    description: 'Coconut rolls',
    image: 'https://images.pexels.com/photos/18488297/pexels-photo-18488297.jpeg?w=500',
    prices: [
      { weight: '½ kg', price: 319 },
      { weight: '1kg', price: 639 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Homemade Style'
  },
  {
    id: 12,
    name: 'Kajjikayalu',
    category: 'sweets',
    description: 'Sweet pastry',
    image: 'https://images.pexels.com/photos/8887249/pexels-photo-8887249.jpeg?w=500',
    prices: [
      { weight: '½ kg', price: 399 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: false,
    isNew: true,
    tag: 'Festival Delight'
  },
  {
    id: 13,
    name: 'Pottu Minapa Sunnundalu',
    category: 'sweets',
    description: 'Urad dal laddu',
    image: 'https://images.pexels.com/photos/8886997/pexels-photo-8886997.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 899 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Traditional Taste'
  },
  {
    id: 14,
    name: 'Nuvvulu Laddu',
    category: 'sweets',
    description: 'Sesame laddu',
    image: 'https://images.unsplash.com/photo-1645453014906-7f2874408d8d?w=500',
    prices: [
      { weight: '½ kg', price: 399 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Power Packed'
  },
  {
    id: 15,
    name: 'Bhoondi Chekka',
    category: 'sweets',
    description: 'Sweet boondi',
    image: 'https://images.pexels.com/photos/8887010/pexels-photo-8887010.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 169 },
      { weight: '½ kg', price: 329 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Light Sweet'
  },
  {
    id: 16,
    name: 'Chalimidi',
    category: 'sweets',
    description: 'Traditional sweet',
    image: 'https://images.pexels.com/photos/13220344/pexels-photo-13220344.jpeg?w=500',
    prices: [
      { weight: '½ kg', price: 299 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Classic'
  },
  {
    id: 17,
    name: 'Sweet Gavvalu',
    category: 'sweets',
    description: 'Sweet shell snack',
    image: 'https://images.unsplash.com/photo-1635952346904-95f2ccfcd029?w=500',
    prices: [
      { weight: '¼ kg', price: 159 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Crunchy Sweet'
  },
  {
    id: 18,
    name: 'Flax Seeds Laddu',
    category: 'sweets',
    description: 'Healthy flax seeds',
    image: 'https://images.unsplash.com/photo-1605194000384-439c3ced8d15?w=500',
    prices: [
      { weight: '½ kg', price: 399 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: false,
    isNew: true,
    tag: 'Super Food'
  },

  // Hot Items (9 items)
  {
    id: 19,
    name: 'Atukullu Mixture',
    category: 'hot-items',
    description: 'Spicy poha mixture',
    image: 'https://images.unsplash.com/photo-1613764816537-a43baeb559c1?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Crispy & Spicy'
  },
  {
    id: 20,
    name: 'Hot Gavvalu',
    category: 'hot-items',
    description: 'Crispy shell snack',
    image: 'https://images.unsplash.com/photo-1683533678033-f5d60f0a3437?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Crunchy Treat'
  },
  {
    id: 21,
    name: 'Hot Kajalu',
    category: 'hot-items',
    description: 'Spicy kajalu snack',
    image: 'https://images.unsplash.com/photo-1589786742305-f24d19eedbe5?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Spicy Snack'
  },
  {
    id: 22,
    name: 'Karapusa',
    category: 'hot-items',
    description: 'Spicy puffed rice',
    image: 'https://images.unsplash.com/photo-1631788012442-633d4f91ad31?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Light Snack'
  },
  {
    id: 23,
    name: 'Palli Pakodi',
    category: 'hot-items',
    description: 'Peanut pakoda',
    image: 'https://images.unsplash.com/photo-1631788012420-a0d6a3cfcdfb?w=500',
    prices: [
      { weight: '¼ kg', price: 159 },
      { weight: '1kg', price: 639 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Crunchy'
  },
  {
    id: 24,
    name: 'Ragi Chakralu',
    category: 'hot-items',
    description: 'Finger millet murukku',
    image: 'https://images.pexels.com/photos/5835026/pexels-photo-5835026.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Healthy'
  },
  {
    id: 25,
    name: 'Ragi Kara Bundhi',
    category: 'hot-items',
    description: 'Spicy ragi boondi',
    image: 'https://images.unsplash.com/photo-1671981200629-014c03829abb?w=500',
    prices: [
      { weight: '¼ kg', price: 174 },
      { weight: '1kg', price: 699 }
    ],
    isBestSeller: false,
    isNew: true,
    tag: 'New Item'
  },
  {
    id: 26,
    name: 'Ribbon Pakodi',
    category: 'hot-items',
    description: 'Ribbon shaped snack',
    image: 'https://images.pexels.com/photos/7717492/pexels-photo-7717492.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Tea Time'
  },
  {
    id: 27,
    name: 'Kaju Masala',
    category: 'hot-items',
    description: 'Spicy cashews',
    image: 'https://images.unsplash.com/photo-1726771517475-e7acdd34cd8a?w=500',
    prices: [
      { weight: '¼ kg', price: 349 },
      { weight: '1kg', price: 1399 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Premium Snack'
  },

  // Snacks (3 items)
  {
    id: 28,
    name: 'Bhondi',
    category: 'snacks',
    description: 'Boondi snack',
    image: 'https://images.unsplash.com/photo-1613764816537-a43baeb559c1?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Light Snack'
  },
  {
    id: 29,
    name: 'Masala Chekkalu',
    category: 'snacks',
    description: 'Spicy rice crackers',
    image: 'https://images.unsplash.com/photo-1683533678033-f5d60f0a3437?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Crispy'
  },
  {
    id: 30,
    name: 'Ragi Masala Chekkalu',
    category: 'snacks',
    description: 'Healthy ragi crackers',
    image: 'https://images.pexels.com/photos/5835026/pexels-photo-5835026.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '½ kg', price: 499 }
    ],
    isBestSeller: false,
    isNew: true,
    tag: 'Nutritious'
  },

  // Veg Pickles (9 items)
  {
    id: 31,
    name: 'Tomato Pickle',
    category: 'pickles',
    description: 'Tangy tomato pickle',
    image: 'https://images.unsplash.com/photo-1617854307432-13950e24ba07?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Homestyle'
  },
  {
    id: 32,
    name: 'Allam Pickle',
    category: 'pickles',
    description: 'Ginger pickle',
    image: 'https://images.unsplash.com/photo-1601702538934-efffab67ab65?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Spicy Delight'
  },
  {
    id: 33,
    name: 'Mango Pickle',
    category: 'pickles',
    description: 'Classic mango pickle',
    image: 'https://images.unsplash.com/photo-1664791461482-79f5deee490f?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'All Time Favorite'
  },
  {
    id: 34,
    name: 'Pandu Mirchi',
    category: 'pickles',
    description: 'Green chili pickle',
    image: 'https://images.pexels.com/photos/12392833/pexels-photo-12392833.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Extra Spicy'
  },
  {
    id: 35,
    name: 'Gongura Pickle',
    category: 'pickles',
    description: 'Sorrel leaves pickle',
    image: 'https://images.unsplash.com/photo-1617854307432-13950e24ba07?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Andhra Special'
  },
  {
    id: 36,
    name: 'Pandu Mirchi Gongura',
    category: 'pickles',
    description: 'Chili gongura mix',
    image: 'https://images.unsplash.com/photo-1601702538934-efffab67ab65?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Special Mix'
  },
  {
    id: 37,
    name: 'Lemon Pickle',
    category: 'pickles',
    description: 'Tangy lemon pickle',
    image: 'https://images.pexels.com/photos/12392833/pexels-photo-12392833.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Fresh & Tangy'
  },
  {
    id: 38,
    name: 'Amla Pickle',
    category: 'pickles',
    description: 'Gooseberry pickle',
    image: 'https://images.unsplash.com/photo-1664791461482-79f5deee490f?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Healthy'
  },
  {
    id: 39,
    name: 'Amla Tokku',
    category: 'pickles',
    description: 'Gooseberry peel pickle',
    image: 'https://images.unsplash.com/photo-1617854307432-13950e24ba07?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Traditional'
  },

  // Powders (11 items)
  {
    id: 40,
    name: 'Kandi Podi',
    category: 'powders',
    description: 'Lentil powder',
    image: 'https://images.unsplash.com/photo-1716816211590-c15a328a5ff0?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Traditional Blend'
  },
  {
    id: 41,
    name: 'Kakarakaya Karam',
    category: 'powders',
    description: 'Bitter gourd spice',
    image: 'https://images.unsplash.com/photo-1650559347569-09a6bbed5f28?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Unique Taste'
  },
  {
    id: 42,
    name: 'Kobbari Karam',
    category: 'powders',
    description: 'Coconut spice powder',
    image: 'https://images.unsplash.com/photo-1647532198387-d28b32575986?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Aromatic'
  },
  {
    id: 43,
    name: 'Flax Seeds Powder',
    category: 'powders',
    description: 'Healthy flax powder',
    image: 'https://images.unsplash.com/photo-1704650312191-005ab02786f5?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: false,
    isNew: true,
    tag: 'Super Food'
  },
  {
    id: 44,
    name: 'Munagaku Karam Podi',
    category: 'powders',
    description: 'Drumstick leaves powder',
    image: 'https://images.unsplash.com/photo-1702041295331-840d4d9aa7c9?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Nutritious'
  },
  {
    id: 45,
    name: 'Nalla Karam Podi',
    category: 'powders',
    description: 'Black sesame powder',
    image: 'https://images.unsplash.com/photo-1704650312022-ed1a76dbed1b?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Traditional'
  },
  {
    id: 46,
    name: 'Pudina Podi',
    category: 'powders',
    description: 'Mint powder',
    image: 'https://images.pexels.com/photos/4397255/pexels-photo-4397255.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Refreshing'
  },
  {
    id: 47,
    name: 'Dhaniyala Podi',
    category: 'powders',
    description: 'Coriander powder',
    image: 'https://images.unsplash.com/photo-1586137712370-9b450509c587?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Aromatic'
  },
  {
    id: 48,
    name: 'Karuvepaku Podi',
    category: 'powders',
    description: 'Curry leaves powder',
    image: 'https://images.pexels.com/photos/10219670/pexels-photo-10219670.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Flavorful'
  },
  {
    id: 49,
    name: 'Nuvvula Podi',
    category: 'powders',
    description: 'Sesame powder',
    image: 'https://images.unsplash.com/photo-1704650312022-ed1a76dbed1b?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Healthy Mix'
  },
  {
    id: 50,
    name: 'Idly Karam Podi',
    category: 'powders',
    description: 'Idli chutney powder',
    image: 'https://images.unsplash.com/photo-1698557048177-a460bb415177?w=500',
    prices: [
      { weight: '¼ kg', price: 249 },
      { weight: '1kg', price: 999 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Breakfast Special'
  },
  {
    id: 51,
    name: 'Sprouted Ragi Powder',
    category: 'powders',
    description: 'Healthy ragi powder',
    image: 'https://images.pexels.com/photos/4198417/pexels-photo-4198417.jpeg?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 599 }
    ],
    isBestSeller: false,
    isNew: true,
    tag: 'Health Mix'
  },

  // Spices (4 items)
  {
    id: 52,
    name: 'Sambar Powder',
    category: 'spices',
    description: 'Authentic sambar masala',
    image: 'https://images.unsplash.com/photo-1716816211590-c15a328a5ff0?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: true,
    isNew: false,
    tag: 'Essential Spice'
  },
  {
    id: 53,
    name: 'Special Rasam Powder',
    category: 'spices',
    description: 'Aromatic rasam masala',
    image: 'https://images.unsplash.com/photo-1650559347569-09a6bbed5f28?w=500',
    prices: [
      { weight: '¼ kg', price: 199 },
      { weight: '1kg', price: 799 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Traditional Taste'
  },
  {
    id: 54,
    name: 'Dhaniya Powder',
    category: 'spices',
    description: 'Coriander powder',
    image: 'https://images.unsplash.com/photo-1702041295331-840d4d9aa7c9?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 499 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Pure'
  },
  {
    id: 55,
    name: 'Pulusu Podi',
    category: 'spices',
    description: 'Tamarind curry powder',
    image: 'https://images.unsplash.com/photo-1698557048177-a460bb415177?w=500',
    prices: [
      { weight: '¼ kg', price: 149 },
      { weight: '1kg', price: 499 }
    ],
    isBestSeller: false,
    isNew: false,
    tag: 'Tangy'
  },
];

export const deliveryLocations = [
  { name: 'Guntur', charge: 49 },
  { name: 'Vijayawada', charge: 99 },
  { name: 'Hyderabad', charge: 149 },
  { name: 'Visakhapatnam', charge: 199 },
  { name: 'Tirupati', charge: 149 },
  { name: 'Other', charge: 199 },
];

export const testimonials = [
  {
    id: 1,
    name: 'Lakshmi Devi',
    location: 'Guntur',
    rating: 5,
    comment: 'Amazing quality! The laddus taste just like homemade. Highly recommended!',
    avatar: 'https://i.pravatar.cc/150?img=1'
  },
  {
    id: 2,
    name: 'Ramesh Kumar',
    location: 'Vijayawada',
    rating: 5,
    comment: 'Fresh products and authentic taste. The pickles are exceptional!',
    avatar: 'https://i.pravatar.cc/150?img=12'
  },
  {
    id: 3,
    name: 'Saroja Rani',
    location: 'Hyderabad',
    rating: 5,
    comment: 'Best traditional sweets I have ever tasted. Fast delivery too!',
    avatar: 'https://i.pravatar.cc/150?img=5'
  },
];
