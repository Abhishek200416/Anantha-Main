import React from 'react';
import { categories } from '../mock';

const CategoryFilter = ({ selectedCategory, onSelectCategory }) => {
  return (
    <div className="bg-white shadow-md sticky top-[72px] z-40 py-4">
      <div className="container mx-auto px-4">
        <div className="flex overflow-x-auto space-x-3 pb-2 scrollbar-hide">
          {categories.map(category => (
            <button
              key={category.id}
              onClick={() => onSelectCategory(category.id)}
              className={`px-6 py-3 rounded-full font-medium whitespace-nowrap transition-all ${
                selectedCategory === category.id
                  ? 'bg-gradient-to-r from-orange-500 to-red-500 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {category.name}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CategoryFilter;