import React, { useState, useEffect } from 'react';
import { Trash2, Tag, Plus, Minus, Package } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import PaymentModal from './PaymentModal';

// Interfaces for type safety
interface CartTopping {
  id?: number;
  topping_id: number;
  topping_name?: string;
  quantity: number;
  price: number;
  order_item_id?: number;
}

interface CartItem {
  cart_item_id: number;
  pizza_id: number;
  pizza_name: string;
  quantity: number;
  item_price: number;
  toppings: CartTopping[];
}

interface CartData {
  cart_id: number;
  items: CartItem[];
  total_price: number;
  discounted_price: number;
}

interface Coupon {
  id: number;
  code: string;
  discount: number;
  description: string;
  expiry_date: string;
}

interface CartProps {
  accessToken: string | null;
}

const Cart: React.FC<CartProps> = ({ accessToken }) => {
  const navigate = useNavigate();
  const [cartData, setCartData] = useState<CartData | null>(null);
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [updateLoading, setUpdateLoading] = useState<number | null>(null);

  // Fetch cart data
  const fetchCart = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/cart', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch cart');
      }

      const data = await response.json();
      setCartData(data.data);
    } catch (err) {
      console.error('Error fetching cart:', err);
      setError('Failed to load cart');
    } finally {
      setLoading(false);
    }
  };

  // Fetch available coupons
  const fetchCoupons = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/coupons', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch coupons');
      }

      const data = await response.json();
      setCoupons(data.data || []);
    } catch (err) {
      console.error('Error fetching coupons:', err);
    }
  };

  // Initial data fetch
  useEffect(() => {
    if (accessToken) {
      fetchCart();
      fetchCoupons();
    }
  }, [accessToken]);

  const updateItemQuantity = async (item: CartItem, isIncrement: boolean) => {
    setUpdateLoading(item.cart_item_id);
  
    try {
      // Calculate the new quantity based on increment/decrement
      const quantityChange = isIncrement ? 1 : -1;
      // Prevent negative quantities
  
      const response = await fetch('http://localhost:8000/api/cart/items', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pizza_id: item.pizza_id,
          quantity: quantityChange, // Use the updated quantity
          toppings: item.toppings.map(t => ({
            topping_id: t.topping_id,
            quantity: quantityChange, // Include topping quantities as-is
          })),
        }),
      });
  
      if (!response.ok) {
        throw new Error('Failed to update quantity');
      }
  
      await fetchCart(); // Refresh cart to reflect changes
    } catch (err) {
      console.error('Error updating quantity:', err);
      setError('Failed to update quantity');
    } finally {
      setUpdateLoading(null);
    }
  };
  

  // Remove item from cart
  const removeCartItem = async (itemId: number) => {
    try {
      const response = await fetch(`http://localhost:8000/api/cart/items/${itemId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to remove item');
      }

      await fetchCart(); // Refresh cart after removal
      
      // If it was the last item, the API might have deleted the cart
      if (response.status === 200) {
        const data = await response.json();
        if (data.message.includes("cart deleted")) {
          setCartData(null);
        }
      }
    } catch (err) {
      console.error('Error removing item:', err);
      setError('Failed to remove item');
    }
  };

  // Apply coupon to cart
  const applyCoupon = async (code: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/cart/coupons?cart_coupon=${code}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to apply coupon');
      }

      await fetchCart(); // Refresh cart data
    } catch (err) {
      console.error('Error applying coupon:', err);
      setError('Failed to apply coupon');
    }
  };

  // Remove applied coupon
  const removeCoupon = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/cart/coupons/remove', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to remove coupon');
      }

      await fetchCart(); // Refresh cart after removing coupon
    } catch (err) {
      console.error('Error removing coupon:', err);
      setError('Failed to remove coupon');
    }
  };
  const handleCheckout = () => {
    setShowPaymentModal(true);
  };
  const handlePaymentSuccess = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/cart/checkout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Checkout failed');
      }

      // Clear cart data
      setCartData(null);
      setShowPaymentModal(false);
      
      // Show success message and redirect to orders
      alert('Order placed successfully!');
      navigate('/orders');
    } catch (err) {
      console.error('Error during checkout:', err);
      setError('Checkout failed');
      setShowPaymentModal(false);
    }
  };

  const handlePaymentError = (message: string) => {
    setError(message);
    setShowPaymentModal(false);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-red-600 text-center p-4">
          <p>{error}</p>
          <button 
            onClick={fetchCart}
            className="mt-2 text-sm text-red-600 hover:text-red-700 underline"
          >
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (!cartData || cartData.items.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Your Cart</h2>
        <div className="text-center py-8">
          <Package size={48} className="mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">Your cart is empty</p>
          <button 
            onClick={() => navigate('/menu')}
            className="mt-4 text-red-600 hover:text-red-700 underline"
          >
            Continue Shopping
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-6">Your Cart</h2>

{/* Cart Items */}
<div className="space-y-4 mb-6">
  {cartData.items.map((item) => (
    <div key={item.cart_item_id} className="flex items-center justify-between border-b pb-4">
      <div className="flex-1">
        <h3 className="font-semibold">{item.pizza_name || `Pizza #${item.pizza_id}`}</h3>
        <p className="text-gray-600">Price: ₹{item.item_price.toFixed(2)}</p>
        <div className="flex items-center space-x-4 mt-2">
          <div className="flex items-center space-x-2">
            <button 
              onClick={() => updateItemQuantity(item, false)}
              className="p-1 rounded-full hover:bg-gray-100 disabled:opacity-50"
              disabled={updateLoading === item.cart_item_id || item.quantity <= 1}
            >
              <Minus size={16} />
            </button>
            <span className="font-medium min-w-[20px] text-center">{item.quantity}</span>
            <button 
              onClick={() => updateItemQuantity(item, true)}
              className="p-1 rounded-full hover:bg-gray-100 disabled:opacity-50"
              disabled={updateLoading === item.cart_item_id}
            >
              <Plus size={16} />
            </button>
          </div>
          <button
            onClick={() => removeCartItem(item.cart_item_id)}
            className="text-red-600 hover:text-red-700 disabled:opacity-50"
            disabled={updateLoading === item.cart_item_id}
          >
            <Trash2 size={16} />
          </button>
        </div>
        {item.toppings.length > 0 && (
          <div className="text-sm text-gray-500 mt-1">
            <p>Toppings:</p>
            <ul className="list-disc pl-5">
              {item.toppings.map(t => (
                <li key={t.topping_id}>
                  {`${t.quantity}x ${t.topping_name || `Topping #${t.topping_id}`}`} 
                  — ₹{t.price.toFixed(2)}
                </li>
              ))}
            </ul>
            <p className="mt-1 font-medium">
              Total Topping Price: ₹
              {item.toppings.reduce((acc, t) => acc + t.price, 0).toFixed(2)}
            </p>
          </div>
        )}
      </div>
      <div className="text-lg font-semibold">
        <div className="flex items-center">
          ₹{((item.item_price * item.quantity) + item.toppings.reduce((acc, t) => acc + t.price, 0)).toFixed(2)}
          {updateLoading === item.cart_item_id && (
            <div className="ml-2 w-4 h-4 border-2 border-red-600 border-t-transparent rounded-full animate-spin"></div>
          )}
        </div>
      </div>
    </div>
  ))}
</div>

      {/* Applied Coupon */}
      {cartData.discounted_price < cartData.total_price && (
        <div className="flex justify-between items-center mb-6 bg-green-50 p-4 rounded-lg">
          <div className="flex-1">
            <span className="font-semibold text-green-700">Coupon Applied</span>
            <p className="text-sm text-green-600">
              You saved: ₹{(cartData.total_price - cartData.discounted_price).toFixed(2)}
            </p>
          </div>
          <button
            onClick={removeCoupon}
            className="text-red-600 hover:text-red-700 text-sm flex items-center"
          >
            Remove <Trash2 className="ml-1" size={16} />
          </button>
        </div>
      )}

      {/* Available Coupons */}
      {coupons.length > 0 && cartData.discounted_price === cartData.total_price && (
        <div className="mb-6">
          <h3 className="text-lg font-semibold mb-3">Available Coupons</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {coupons.map((coupon) => (
              <div key={coupon.id} className="border rounded-lg p-4 hover:border-red-200">
                <div className="flex justify-between items-start">
                  <div>
                    <div className="flex items-center space-x-2">
                      <Tag size={16} className="text-red-600" />
                      <span className="font-bold text-lg">{coupon.code}</span>
                    </div>
                    <p className="text-sm text-gray-600">{coupon.description}</p>
                    <p className="text-sm text-gray-500">
                      Expires: {new Date(coupon.expiry_date).toLocaleString()}
                    </p>
                  </div>
                  <button
                    onClick={() => applyCoupon(coupon.code)}
                    className="bg-red-600 text-white px-3 py-1 rounded-md hover:bg-red-700 text-sm"
                  >
                    Apply
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

{/* Cart Summary */}
<div className="border-t pt-4 space-y-2">
        <div className="flex justify-between text-lg">
          <span>Subtotal:</span>
          <span>₹{cartData?.total_price.toFixed(2)}</span>
        </div>
        {cartData?.discounted_price < cartData?.total_price && (
          <div className="flex justify-between text-lg text-green-600">
            <span>Discounted Price:</span>
            <span>₹{cartData?.discounted_price.toFixed(2)}</span>
          </div>
        )}
        <button
          onClick={handleCheckout}
          className="w-full bg-red-600 text-white py-3 rounded-lg hover:bg-red-700 font-semibold mt-4"
        >
          Proceed to Payment (₹{(cartData?.discounted_price || cartData?.total_price || 0).toFixed(2)})
        </button>
      </div>

      {/* Payment Modal */}
      {showPaymentModal && cartData && (
        <PaymentModal
          amount={cartData.discounted_price || cartData.total_price}
          onClose={() => setShowPaymentModal(false)}
          onSuccess={handlePaymentSuccess}
          onError={handlePaymentError}
        />
      )}
    </div>
  );
}
export default Cart;