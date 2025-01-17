import React, { useState, useEffect } from 'react';
import { Package } from 'lucide-react';
import { fetchWithAuth } from '../services/api';
import { useNavigate } from 'react-router-dom';

interface OrderTopping {
  order_item_id: number;
  topping_id: number;
  topping_name: string;
  quantity: number;
  price: number;
}

interface OrderItem {
  id: number;
  pizza_id: number;
  pizza_name: string;
  quantity: number;
  item_price: number;
  toppings: OrderTopping[];
  total_topping_price: number;
}

interface OrderData {
  order_id: number;
  total_price: number;
  created_at: string;
  status: string | null;
  items: OrderItem[];
}

function Orders() {
  const [orders, setOrders] = useState<OrderData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [noOrdersMessage, setNoOrdersMessage] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await fetchWithAuth('/api/orders/my-orders');
        const result = await response.json();

        if (result.message === 'User orders retrieved successfully' && result.data.data) {
          setOrders(result.data.data);
          setNoOrdersMessage(result.data.data.length === 0 ? 'You have no orders yet.' : null);
        } else {
          setOrders([]);
          setNoOrdersMessage('You have no orders yet.');
        }
      } catch (error) {
        console.error('Error fetching orders:', error);
        setError('Failed to load orders');
        setOrders([]);
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
    
    // Refresh orders every 10 seconds if there are non-completed orders
    const intervalId = setInterval(() => {
      if (orders.some(order => order.status !== 'Completed')) {
        fetchOrders();
      }
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, []);

  const getStatusColor = (status: string | null) => {
    const statusClasses: Record<string, string> = {
      'Completed': 'bg-green-100 text-green-800',
      'Ready for Pickup': 'bg-purple-100 text-purple-800',
      'Baking': 'bg-orange-100 text-orange-800',
      'Preparing': 'bg-blue-100 text-blue-800',
      'Received': 'bg-gray-100 text-gray-800',
    };

    return statusClasses[status || 'Pending'] || 'bg-yellow-100 text-yellow-800';
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
        <p className="text-red-600 text-center">{error}</p>
      </div>
    );
  }

  if (noOrdersMessage) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold mb-4">Your Orders</h2>
        <div className="text-center py-8">
          <Package size={48} className="mx-auto text-gray-400 mb-4" />
          <p className="text-gray-500">{noOrdersMessage}</p>
          <button 
            onClick={() => navigate('/')}
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
      <div className="flex items-center space-x-2 mb-6">
        <Package size={24} className="text-red-600" />
        <h2 className="text-2xl font-bold">Your Orders</h2>
      </div>

      <div className="space-y-6">
        {orders.map((order) => (
          <div 
            key={order.order_id} 
            className="border rounded-lg p-6 hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => navigate(`/orders/${order.order_id}`)}
          >
            <div className="flex justify-between items-start mb-4">
              <div>
                <div className="flex items-center space-x-3">
                  <span className="font-semibold text-lg">Order #{order.order_id}</span>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                    {order.status || 'Pending'}
                  </span>
                </div>
                <p className="text-gray-600 mt-1">
                  Placed on: {new Date(order.created_at).toLocaleString()}
                </p>
              </div>
              <p className="font-semibold text-lg text-red-600">
                ₹{order.total_price.toFixed(2)}
              </p>
            </div>

            <div className="mt-4">
              <h3 className="font-medium mb-2">Order Items:</h3>
              <div className="space-y-3">
                {order.items.map((item) => (
                  <div key={item.id} className="bg-gray-50 rounded p-3">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="font-medium">{item.pizza_name}</p>
                        <p className="text-gray-600">Quantity: {item.quantity}</p>
                        <p className="text-gray-600">Price: ₹{item.item_price}</p>
                        {item.toppings.map((topping) => (
                          <p key={topping.topping_id} className="text-sm text-gray-500 ml-4">
                            • {topping.topping_name} × {topping.quantity} (₹{topping.price})
                          </p>
                        ))}
                        {item.total_topping_price > 0 && (
                          <p className="text-sm text-gray-600 ml-4 mt-1">
                            Total toppings: ₹{item.total_topping_price}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Orders;