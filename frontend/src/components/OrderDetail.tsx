import React, { useState, useEffect } from 'react';
import { Package, ArrowLeft } from 'lucide-react';
import { fetchWithAuth } from '../services/api';
import { useParams, useNavigate } from 'react-router-dom';

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

function OrderDetail() {
  const [orderData, setOrderData] = useState<OrderData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { orderId } = useParams();
  const navigate = useNavigate();

  const fetchOrderData = async () => {
    try {
      const response = await fetchWithAuth(`/api/orders/${orderId}`);
      const result = await response.json();
      
      if (result.message === "Order retrieved successfully") {
        setOrderData(result.data);
      } else {
        setError('Failed to load order details');
      }
    } catch (error) {
      console.error('Error fetching order:', error);
      setError('Failed to load order details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOrderData();
    
    // Set up polling for status updates every 10 seconds if order is not completed
    const intervalId = setInterval(() => {
      if (orderData && orderData.status !== 'Completed') {
        fetchOrderData();
      }
    }, 5000);
    
    return () => clearInterval(intervalId);
  }, [orderId, orderData?.status]);

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

  if (error || !orderData) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-red-600 text-center">{error}</p>
        <button 
          onClick={() => navigate('/orders')}
          className="mt-4 text-red-600 hover:text-red-700 flex items-center justify-center space-x-2"
        >
          <ArrowLeft size={20} />
          <span>Back to Orders</span>
        </button>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-2">
          <Package size={24} className="text-red-600" />
          <h2 className="text-2xl font-bold">Order Details</h2>
        </div>
        <button 
          onClick={() => navigate('/orders')}
          className="text-red-600 hover:text-red-700 flex items-center space-x-2"
        >
          <ArrowLeft size={20} />
          <span>Back to Orders</span>
        </button>
      </div>

      <div className="border rounded-lg p-6">
        <div className="flex justify-between items-start mb-6">
          <div>
            <div className="flex items-center space-x-3 mb-2">
              <span className="font-semibold text-lg">Order #{orderData.order_id}</span>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(orderData.status)}`}>
                {orderData.status || 'Pending'}
              </span>
            </div>
            <p className="text-gray-600">
              Placed on: {new Date(orderData.created_at).toLocaleString()}
            </p>
          </div>
          <p className="font-semibold text-lg text-red-600">
            ₹{orderData.total_price.toFixed(2)}
          </p>
        </div>

        <div className="mt-6">
          <h3 className="font-medium mb-3">Order Items:</h3>
          <div className="space-y-4">
            {orderData.items.map((item) => (
              <div key={item.id} className="bg-gray-50 rounded-lg p-4">
                <div className="flex justify-between items-start">
                  <div>
                    <p className="font-medium">{item.pizza_name}</p>
                    <p className="text-gray-600 mt-1">Quantity: {item.quantity}</p>
                    <p className="text-gray-600">Price: ₹{item.item_price}</p>
                    {item.toppings.map((topping) => (
                      <p key={topping.topping_id} className="text-sm text-gray-500 mt-2 ml-4">
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

        <div className="mt-6 pt-6 border-t">
          <h3 className="font-medium mb-3">Order Status Timeline</h3>
          <div className="space-y-3">
            {['Received', 'Preparing', 'Baking', 'Ready for Pickup', 'Completed'].map((status) => {
              const isCurrentStatus = orderData.status === status;
              const isPastStatus = false; // You can implement this based on your status logic
              
              return (
                <div 
                  key={status}
                  className={`flex items-center space-x-3 ${isCurrentStatus ? 'text-red-600' : 'text-gray-500'}`}
                >
                  <div className={`w-3 h-3 rounded-full ${
                    isCurrentStatus ? 'bg-red-600' : 
                    isPastStatus ? 'bg-green-500' : 
                    'bg-gray-300'
                  }`} />
                  <span className={isCurrentStatus ? 'font-medium' : ''}>{status}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}

export default OrderDetail;