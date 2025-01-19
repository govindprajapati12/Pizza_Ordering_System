import React, { useState, useEffect } from 'react';
import { fetchWithAuth } from '../services/api';
import { 
  Users, Pizza, Cookie, Tag, Package, Plus, Pencil, Trash2, 
  CheckCircle, XCircle,UserPlus
} from 'lucide-react';

// Interfaces
interface User {
  id: number;
  username: string;
  email: string;
  role: string;
}

interface Pizza {
  id: number;
  name: string;
  description: string;
  price: number;
  image: string;
  created_at: string;
}

interface Topping {
  id: number;
  name: string;
  price: number;
  created_at: string;
}

interface Coupon {
  id: number;
  code: string;
  discount: number;
  expiration_date: string;
  usage_limit: number | null;
  created_at: string;
}

interface OrderItem {
  id: number;
  pizza_id: number;
  quantity: number;
}

interface OrderTopping {
  order_item_id: number;
  topping_id: number;
  quantity: number;
}

interface Order {
  order: {
    id: number;
    user_id: number;
    total_price: number;
    created_at: string;
    status: string | null;
  };
  order_items: OrderItem[];
  order_toppings: OrderTopping[];
}

function AdminDashboard() {
  // State
  const [activeTab, setActiveTab] = useState('orders');
  const [users, setUsers] = useState<User[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [pizzas, setPizzas] = useState<Pizza[]>([]);
  const [toppings, setToppings] = useState<Topping[]>([]);
  const [coupons, setCoupons] = useState<Coupon[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pizza form state
  const [newPizza, setNewPizza] = useState({
    name: '',
    description: '',
    price: '',
    image: null as File | null,
  });

  // Topping form state
  const [newTopping, setNewTopping] = useState({
    name: '',
    price: '',
  });

  // Coupon form state
  const [newCoupon, setNewCoupon] = useState({
    code: '',
    discount: '',
    expiration_date: '',
    usage_limit: '',
  });
  //new admin form state
  const [newAdmin, setNewAdmin] = useState({
    name: '',
    email: '',
    password: '',
  });

  // Fetch data
  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [usersRes, ordersRes, pizzasRes, toppingsRes, couponsRes] = await Promise.all([
          fetchWithAuth('http://localhost:8000/api/users'),
          fetchWithAuth('http://localhost:8000/api/orders/all'),
          fetchWithAuth('http://localhost:8000/api/pizzas'),
          fetchWithAuth('http://localhost:8000/api/toppings'),
          fetchWithAuth('http://localhost:8000/api/coupons/all'),
        ]);

        const [usersData, ordersData, pizzasData, toppingsData, couponsData] = await Promise.all([
          usersRes.json(),
          ordersRes.json(),
          pizzasRes.json(),
          toppingsRes.json(),
          couponsRes.json(),
        ]);

        setUsers(usersData.data);
        setOrders(ordersData.data);
        setPizzas(pizzasData.data);
        setToppings(toppingsData.data);
        setCoupons(couponsData.data);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handlers
  const handleUpdateOrderStatus = async (orderId: number, status: string) => {
    try {
      // Send the updated status to the backend
      await fetchWithAuth(`http://localhost:8000/api/orders/${orderId}/status?new_status=${encodeURIComponent(status)}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
      });
  
      // Update the state with the new order status
      setOrders(orders.map(order =>
        order.order.id === orderId
          ? { ...order, order: { ...order.order, status } }
          : order
      ));
    } catch (err) {
      console.error('Error updating order status:', err);
      setError('Failed to update order status');
    }
  };

  const handleCreatePizza = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('name', newPizza.name);
      formData.append('description', newPizza.description);
      formData.append('price', newPizza.price.toString());
      if (newPizza.image) {
        formData.append('file', newPizza.image);
      }
  
      const response = await fetchWithAuth('http://localhost:8000/api/pizzas', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      
      if (result.data) {
        setPizzas(prevPizzas => prevPizzas ? [...prevPizzas, result.data] : [result.data]);
        setNewPizza({ name: '', description: '', price: '', image: null });
      } else {
        setError('Failed to create pizza: No data received');
      }
    } catch (err) {
      console.error('Error creating pizza:', err);
      setError('Failed to create pizza');
    }
  };
  const handleCreateTopping = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetchWithAuth('http://localhost:8000/api/toppings/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newTopping),
      });
      const data = await response.json();
      setToppings([...toppings, data.data]);
      setNewTopping({ name: '', price: ''});
    } catch (err) {
      console.error('Error creating topping:', err);
      setError('Failed to create topping');
    }
  };

  const handleCreateCoupon = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetchWithAuth('http://localhost:8000/api/coupons/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newCoupon),
      });
      const data = await response.json();
      setCoupons([...coupons, data.data]);
      setNewCoupon({ code: '', discount: '', expiration_date: '', usage_limit: '' });
    } catch (err) {
      console.error('Error creating coupon:', err);
      setError('Failed to create coupon');
    }
  };

  const handleDeletePizza = async (id: number) => {
    try {
      await fetchWithAuth(`http://localhost:8000/api/pizzas/${id}`, {
        method: 'DELETE',
      });
      setPizzas(pizzas.filter(pizza => pizza.id !== id));
    } catch (err) {
      console.error('Error deleting pizza:', err);
      setError('Failed to delete pizza');
    }
  };

  const handleDeleteTopping = async (id: number) => {
    try {
      await fetchWithAuth(`http://localhost:8000/api/toppings/${id}`, {
        method: 'DELETE',
      });
      setToppings(toppings.filter(topping => topping.id !== id));
    } catch (err) {
      console.error('Error deleting topping:', err);
      setError('Failed to delete topping');
    }
  };

  const handleDeleteCoupon = async (id: number) => {
    try {
      await fetchWithAuth(`http://localhost:8000/api/coupons/${id}`, {
        method: 'DELETE',
      });
      setCoupons(coupons.filter(coupon => coupon.id !== id));
    } catch (err) {
      console.error('Error deleting coupon:', err);
      setError('Failed to delete coupon');
    }
  };
    // Add handler for creating new admin
    const handleCreateAdmin = async (e: React.FormEvent) => {
      e.preventDefault();
      try {
        const response = await fetchWithAuth('http://localhost:8000/api/create_admin', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(newAdmin),
        });
  
        if (response.ok) {
          // Refresh users list
          const usersRes = await fetchWithAuth('http://localhost:8000/api/users');
          const usersData = await usersRes.json();
          setUsers(usersData.data);
          
          // Reset form
          setNewAdmin({
            name: '',
            email: '',
            password: '',
          });
          
          setError(null);
        } else {
          const errorData = await response.json();
          setError(errorData.detail || 'Failed to create admin');
        }
      } catch (err) {
        console.error('Error creating admin:', err);
        setError('Failed to create admin');
      }
    };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold mb-6">Admin Dashboard</h2>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {/* Navigation Tabs */}
      <div className="flex space-x-4 mb-6 border-b">
        <button
          onClick={() => setActiveTab('orders')}
          className={`pb-2 px-4 ${
            activeTab === 'orders'
              ? 'border-b-2 border-red-600 text-red-600'
              : 'text-gray-500'
          }`}
        >
          <div className="flex items-center space-x-2">
            <Package size={20} />
            <span>Orders</span>
          </div>
        </button>
        <button
          onClick={() => setActiveTab('users')}
          className={`pb-2 px-4 ${
            activeTab === 'users'
              ? 'border-b-2 border-red-600 text-red-600'
              : 'text-gray-500'
          }`}
        >
          <div className="flex items-center space-x-2">
            <Users size={20} />
            <span>Users</span>
          </div>
        </button>
        <button
          onClick={() => setActiveTab('pizzas')}
          className={`pb-2 px-4 ${
            activeTab === 'pizzas'
              ? 'border-b-2 border-red-600 text-red-600'
              : 'text-gray-500'
          }`}
        >
          <div className="flex items-center space-x-2">
            <Pizza size={20} />
            <span>Pizzas</span>
          </div>
        </button>
        <button
          onClick={() => setActiveTab('toppings')}
          className={`pb-2 px-4 ${
            activeTab === 'toppings'
              ? 'border-b-2 border-red-600 text-red-600'
              : 'text-gray-500'
          }`}
        >
          <div className="flex items-center space-x-2">
            <Cookie size={20} />
            <span>Toppings</span>
          </div>
        </button>
        <button
          onClick={() => setActiveTab('coupons')}
          className={`pb-2 px-4 ${
            activeTab === 'coupons'
              ? 'border-b-2 border-red-600 text-red-600'
              : 'text-gray-500'
          }`}
        >
          <div className="flex items-center space-x-2">
            <Tag size={20} />
            <span>Coupons</span>
          </div>
        </button>
      </div>

      {/* Content */}
      <div className="mt-6">
        {/* Orders Tab */}
        {activeTab === 'orders' && (
          <div className="space-y-6">
            {orders.map((order) => (
              <div key={order.order.id} className="border rounded-lg p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">
                      Order #{order.order.id}
                    </h3>
                    <p className="text-gray-600">
                      User ID: {order.order.user_id}
                    </p>
                    <p className="text-gray-600">
                      Date: {new Date(order.order.created_at).toLocaleString()}
                    </p>
                    <p className="font-medium text-red-600">
                      Total: ₹{order.order.total_price.toFixed(2)}
                    </p>
                  </div>
                  <select
                  value={order.order.status || 'Received'} // Default to 'Received' if no status
                  onChange={(e) => handleUpdateOrderStatus(order.order.id, e.target.value)}
                  className="border rounded-md px-3 py-1"
                  >
                  <option value="Received">Received</option>
                  <option value="Preparing">Preparing</option>
                  <option value="Baking">Baking</option>
                  <option value="Ready for Pickup">Ready for Pickup</option>
                  <option value="Completed">Completed</option>
                  </select>                
                  </div>
                <div className="space-y-2">
                  {order.order_items.map((item) => (
                    <div key={item.id} className="bg-gray-50 p-3 rounded">
                      <p>Pizza #{item.pizza_id} × {item.quantity}</p>
                      {order.order_toppings
                        .filter((t) => t.order_item_id === item.id)
                        .map((topping) => (
                          <p key={topping.topping_id} className="text-sm text-gray-600 ml-4">
                            • Topping #{topping.topping_id} × {topping.quantity}
                          </p>
                        ))}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'users' && (
          <div>
            {/* Create Admin Form */}
            <form onSubmit={handleCreateAdmin} className="mb-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-2 mb-4">
                <UserPlus size={20} className="text-red-600" />
                <h3 className="text-lg font-semibold">Create New Admin</h3>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input
                  type="text"
                  placeholder="Name"
                  value={newAdmin.name}
                  onChange={(e) => setNewAdmin({ ...newAdmin, name: e.target.value })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={newAdmin.email}
                  onChange={(e) => setNewAdmin({ ...newAdmin, email: e.target.value })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                <input
                  type="password"
                  placeholder="Password"
                  value={newAdmin.password}
                  onChange={(e) => setNewAdmin({ ...newAdmin, password: e.target.value })}
                  className="border rounded-md px-3 py-2"
                  required
                />
              </div>
              <button
                type="submit"
                className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 flex items-center space-x-2"
              >
                <UserPlus size={20} />
                <span>Create Admin</span>
              </button>
            </form>

            {/* Users Table */}
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Username
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {users.map((user) => (
                    <tr key={user.id}>
                      <td className="px-6 py-4 whitespace-nowrap">{user.id}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{user.username}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{user.email}</td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          user.role === 'admin' 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-green-100 text-green-800'
                        }`}>
                          {user.role}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
        {/* Pizzas Tab */}
        {activeTab === 'pizzas' && (
          <div>
            <form onSubmit={handleCreatePizza} className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Add New Pizza</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Pizza Name"
                  value={newPizza.name}
                  onChange={(e) => setNewPizza({ ...newPizza, name: e.target.value })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                <input
                  type="number"
                  placeholder="Price"
                  min={0}
                  value={newPizza.price}
                  onChange={(e) => setNewPizza({ ...newPizza, price: ((e.target.value === '' || e.target.value === null) ? '' : e.target.value) })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                <input
                  type="text"
                  placeholder="Description"
                  value={newPizza.description}
                  onChange={(e) => setNewPizza({ ...newPizza, description: e.target.value })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                <input
                  type="file"
                  accept="image/*"
                  onChange={(e) => setNewPizza({ 
                    ...newPizza, 
                    image: e.target.files ? e.target.files[0] : null 
                  })}
                  className="border rounded-md px-3 py-2"
                  required
                />
              </div>
              <button
                type="submit"
                className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Add Pizza
              </button>
            </form>

            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
              </div>
            ) : error ? (
              <div className="text-center py-8">
                <p className="text-red-600">{error}</p>
              </div>
            ) : !pizzas || pizzas.length === 0 ? (
              <div className="text-center py-8">
                <Pizza size={48} className="mx-auto text-gray-400 mb-4" />
                <p className="text-gray-500">No pizzas available. Add your first pizza above!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {pizzas.map((pizza) => (
                  <div key={pizza.id} className="border rounded-lg overflow-hidden">
                    <img
                      src={`http://localhost:8000${pizza.image}`}
                      alt={pizza.name}
                      className="w-full h-48 object-cover"
                    />
                    <div className="p-4">
                      <h3 className="font-semibold">{pizza.name}</h3>
                      <p className="text-gray-600">{pizza.description}</p>
                      <p className="text-red-600 font-medium">₹{pizza.price}</p>
                      <button
                        onClick={() => handleDeletePizza(pizza.id)}
                        className="mt-2 text-red-600 hover:text-red-800"
                      >
                        <Trash2 size={20} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Toppings Tab */}
        {activeTab === 'toppings' && (
          <div>
            <form onSubmit={handleCreateTopping} className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Add New Topping</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Topping Name"
                  value={newTopping.name}
                  onChange={(e) => setNewTopping({ ...newTopping, name: e.target.value })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                <input
                  type="number"
                  placeholder="Price"
                  min={0}
                  value={newTopping.price}
                  onChange={(e) => setNewTopping({ ...newTopping, price: ((e.target.value === '' || e.target.value === null) ? '' : e.target.value) })}
                  className="border rounded-md px-3 py-2"
                  required
                />
              </div>
              <button
                type="submit"
                className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Add Topping
              </button>
            </form>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {toppings.map((topping) => (
                <div key={topping.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{topping.name}</h3>
                      <p className="text-red-600">₹{topping.price}</p>
                    </div>
                    <button
                      onClick={() => handleDeleteTopping(topping.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Coupons Tab */}
        {activeTab === 'coupons' && (
          <div>
            <form onSubmit={handleCreateCoupon} className="mb-6 p-4 bg-gray-50 rounded-lg">
              <h3 className="text-lg font-semibold mb-4">Add New Coupon</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Coupon Code"
                  value={newCoupon.code}
                  onChange={(e) => setNewCoupon({ ...newCoupon, code: e.target.value })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                {/* <div>
                  <label htmlFor="discount" className="block text-sm font-medium text-gray-700">
                    Discount Amount
                  </label> */}
                <input
                  type="number"
                  placeholder="Discount Amount"
                  value={newCoupon.discount || ''}
                  min={0}
                  onChange={(e) => setNewCoupon({ ...newCoupon, discount: ((e.target.value === '' || e.target.value === null) ? '' : e.target.value) })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                {/* </div> */}
                <input
                  type="date"
                  placeholder="Expiration Date"
                  value={newCoupon.expiration_date}
                  onChange={(e) => setNewCoupon({ ...newCoupon, expiration_date: e.target.value })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                {/* <div>
                  <label htmlFor="usage_limit" className="block text-sm font-medium text-gray-700">
                    Usage Limit
                  </label> */}
                <input
                  type="number"
                  placeholder="Usage Limit"
                  value={newCoupon.usage_limit || ''}
                  min={0}
                  onChange={(e) => setNewCoupon({ ...newCoupon, usage_limit: ((e.target.value === '' || e.target.value === null) ? '' : e.target.value) })}
                  className="border rounded-md px-3 py-2"
                  required
                />
                {/* </div> */}
              </div>
              <button
                type="submit"
                className="mt-4 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700"
              >
                Add Coupon
              </button>
            </form>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {coupons.map((coupon) => (
                <div key={coupon.id} className="border rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="font-semibold">{coupon.code}</h3>
                      <p className="text-red-600">₹{coupon.discount} off</p>
                      <p className="text-sm text-gray-600">
                        Expires: {new Date(coupon.expiration_date).toLocaleDateString()}
                      </p>
                      {coupon.usage_limit && (
                        <p className="text-sm text-gray-600">
                          Usage Limit: {coupon.usage_limit}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => handleDeleteCoupon(coupon.id)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 size={20} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;