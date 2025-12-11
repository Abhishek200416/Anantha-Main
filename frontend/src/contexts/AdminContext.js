import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { products as initialProducts, deliveryLocations as initialLocations } from '../mock';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AdminContext = createContext();

export const useAdmin = () => {
  const context = useContext(AdminContext);
  if (!context) {
    throw new Error('useAdmin must be used within AdminProvider');
  }
  return context;
};

export const AdminProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [products, setProducts] = useState([]);
  const [deliveryLocations, setDeliveryLocations] = useState([]);
  const [states, setStates] = useState([]);
  const [festivalProduct, setFestivalProduct] = useState(null);
  const [orders, setOrders] = useState([]);

  // Fetch products from backend
  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API}/products`);
      // Always use backend data, even if empty
      setProducts(response.data || []);
    } catch (error) {
      console.error('Error fetching products:', error);
      // Set empty array if backend fails
      setProducts([]);
    }
  };

  // Fetch delivery locations from backend
  const fetchDeliveryLocations = async () => {
    try {
      const response = await axios.get(`${API}/locations`);
      setDeliveryLocations(response.data || []);
    } catch (error) {
      console.error('Error fetching delivery locations:', error);
      // Fallback to initial locations if backend fails
      setDeliveryLocations(initialLocations);
    }
  };

  // Load data from localStorage and backend
  useEffect(() => {
    const auth = localStorage.getItem('anantha-admin-auth');
    if (auth === 'true') {
      setIsAuthenticated(true);
    }

    // Fetch products and locations from backend
    fetchProducts();
    fetchDeliveryLocations();

    const savedFestival = localStorage.getItem('anantha-festival');
    if (savedFestival) {
      setFestivalProduct(JSON.parse(savedFestival));
    }

    const savedOrders = localStorage.getItem('anantha-orders');
    if (savedOrders) {
      setOrders(JSON.parse(savedOrders));
    }
  }, []);

  // Note: Products and locations are now managed in backend database, not localStorage

  useEffect(() => {
    if (festivalProduct) {
      localStorage.setItem('anantha-festival', JSON.stringify(festivalProduct));
    } else {
      localStorage.removeItem('anantha-festival');
    }
  }, [festivalProduct]);

  useEffect(() => {
    localStorage.setItem('anantha-orders', JSON.stringify(orders));
  }, [orders]);

  const login = async (email, password) => {
    try {
      // Call backend admin login API
      const response = await axios.post(`${API}/auth/admin-login`, {
        email: email,
        password: password
      });
      
      // Store token and user data
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      localStorage.setItem('user', JSON.stringify(user));
      localStorage.setItem('anantha-admin-auth', 'true');
      
      setIsAuthenticated(true);
      return true;
    } catch (error) {
      console.error('Admin login error:', error);
      return false;
    }
  };

  const logout = () => {
    setIsAuthenticated(false);
    localStorage.removeItem('anantha-admin-auth');
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  };

  const addProduct = async (product) => {
    try {
      const token = localStorage.getItem('token');
      const newProduct = {
        ...product,
        id: `product_${Date.now()}`,
      };
      
      // Save to backend
      await axios.post(`${API}/products`, newProduct, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update local state
      setProducts([...products, newProduct]);
      return newProduct;
    } catch (error) {
      console.error('Error adding product:', error);
      // Fallback to local only
      const newProduct = {
        ...product,
        id: `product_${Date.now()}`,
      };
      setProducts([...products, newProduct]);
      return newProduct;
    }
  };

  const updateProduct = async (id, updatedProduct) => {
    try {
      const token = localStorage.getItem('token');
      
      // Update backend
      await axios.put(`${API}/products/${id}`, updatedProduct, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update local state
      setProducts(products.map(p => p.id === id ? { ...p, ...updatedProduct } : p));
    } catch (error) {
      console.error('Error updating product:', error);
      // Update local only
      setProducts(products.map(p => p.id === id ? { ...p, ...updatedProduct } : p));
    }
  };

  const deleteProduct = async (id) => {
    try {
      const token = localStorage.getItem('token');
      
      // Delete from backend
      await axios.delete(`${API}/products/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update local state
      setProducts(products.filter(p => p.id !== id));
    } catch (error) {
      console.error('Error deleting product:', error);
      // Delete from local only
      setProducts(products.filter(p => p.id !== id));
    }
  };

  const updateDeliveryLocation = async (name, charge, freeDeliveryThreshold = null, state = '') => {
    try {
      const token = localStorage.getItem('token');
      
      // Update individual city settings using new endpoint
      const params = new URLSearchParams();
      if (charge !== undefined && charge !== null) {
        params.append('charge', charge);
      }
      if (freeDeliveryThreshold !== undefined && freeDeliveryThreshold !== null) {
        params.append('free_delivery_threshold', freeDeliveryThreshold);
      }
      
      await axios.put(`${API}/admin/locations/${encodeURIComponent(name)}?${params.toString()}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      // Update local state
      const updatedLocations = deliveryLocations.map(loc =>
        loc.name === name ? { ...loc, charge, free_delivery_threshold: freeDeliveryThreshold, state } : loc
      );
      
      // If location doesn't exist, add it
      const exists = deliveryLocations.find(loc => loc.name === name);
      if (!exists) {
        updatedLocations.push({ name, charge, free_delivery_threshold: freeDeliveryThreshold, state });
      }
      
      setDeliveryLocations(updatedLocations);
      
      return true;
    } catch (error) {
      console.error('Error updating location:', error);
      // Update local state even if backend fails
      const exists = deliveryLocations.find(loc => loc.name === name);
      if (exists) {
        setDeliveryLocations(deliveryLocations.map(loc =>
          loc.name === name ? { ...loc, charge, free_delivery_threshold: freeDeliveryThreshold, state } : loc
        ));
      } else {
        setDeliveryLocations([...deliveryLocations, { name, charge, free_delivery_threshold: freeDeliveryThreshold, state }]);
      }
      return false;
    }
  };

  const deleteDeliveryLocation = async (name) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/admin/locations/${encodeURIComponent(name)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setDeliveryLocations(deliveryLocations.filter(loc => loc.name !== name));
    } catch (error) {
      console.error('Error deleting location:', error);
      // Delete from local only if API fails
      setDeliveryLocations(deliveryLocations.filter(loc => loc.name !== name));
    }
  };

  // Fetch states from backend
  const fetchStates = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(`${API}/admin/states`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStates(response.data);
    } catch (error) {
      console.error('Error fetching states:', error);
    }
  };

  const addState = async (name) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${API}/admin/states`, 
        { name, enabled: true },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      await fetchStates();
    } catch (error) {
      console.error('Error adding state:', error);
      throw error;
    }
  };

  const updateState = async (name, enabled) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API}/admin/states/${encodeURIComponent(name)}`, 
        { name, enabled },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setStates(states.map(state =>
        state.name === name ? { ...state, enabled } : state
      ));
    } catch (error) {
      console.error('Error updating state:', error);
      throw error;
    }
  };

  const deleteState = async (name) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${API}/admin/states/${encodeURIComponent(name)}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setStates(states.filter(state => state.name !== name));
    } catch (error) {
      console.error('Error deleting state:', error);
      throw error;
    }
  };

  const addOrder = async (order) => {
    try {
      // Get user token
      const token = localStorage.getItem('token');
      if (!token) {
        // Create a guest user token if not logged in
        console.warn('No user token found, order will be created as guest');
        throw new Error('Please login or register to place an order');
      }

      // Prepare order data for backend
      const orderData = {
        user_id: 'guest', // Will be overridden by backend with actual user ID
        customer_name: order.customer.name,
        email: order.customer.email,
        phone: order.customer.phone,
        address: order.customer.address,
        doorNo: order.customer.doorNo,
        building: order.customer.building,
        street: order.customer.street,
        city: order.customer.city,
        state: order.customer.state,
        pincode: order.customer.pincode,
        location: order.customer.location,
        items: order.items.map(item => ({
          product_id: item.id,
          name: item.name,
          image: item.image,
          weight: item.weight,
          price: item.price,
          quantity: item.quantity,
          description: item.description || ''
        })),
        subtotal: order.subtotal,
        delivery_charge: order.deliveryCharge,
        total: order.total,
        payment_method: order.paymentMethod,
        payment_sub_method: order.paymentSubMethod
      };

      // Call backend API to create order
      const response = await axios.post(`${API}/orders`, orderData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      // Also save to localStorage for admin viewing
      const localOrder = {
        ...order,
        id: response.data.order_id,
        status: 'Pending',
        orderDate: new Date().toISOString(),
        estimatedDelivery: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
      };
      setOrders([localOrder, ...orders]);

      return {
        id: response.data.order_id,
        ...localOrder
      };
    } catch (error) {
      console.error('Error creating order:', error);
      // Fallback to localStorage if backend fails
      const newOrder = {
        ...order,
        id: Date.now(),
        status: 'Pending',
        orderDate: new Date().toISOString(),
        estimatedDelivery: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
      };
      setOrders([newOrder, ...orders]);
      return newOrder;
    }
  };

  const updateOrderStatus = (id, status) => {
    setOrders(orders.map(order =>
      order.id === id ? { ...order, status } : order
    ));
  };

  return (
    <AdminContext.Provider value={{
      isAuthenticated,
      login,
      logout,
      products,
      fetchProducts,
      addProduct,
      updateProduct,
      deleteProduct,
      deliveryLocations,
      fetchDeliveryLocations,
      updateDeliveryLocation,
      deleteDeliveryLocation,
      states,
      fetchStates,
      addState,
      updateState,
      deleteState,
      festivalProduct,
      setFestivalProduct,
      orders,
      addOrder,
      updateOrderStatus
    }}>
      {children}
    </AdminContext.Provider>
  );
};