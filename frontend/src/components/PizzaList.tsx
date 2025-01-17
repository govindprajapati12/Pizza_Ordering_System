import React, { useState, useEffect } from 'react';
import { Plus } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Pizza {
  id: number;
  name: string;
  description: string;
  price: number;
  image: string;
}

interface Topping {
  id: number;
  name: string;
  price: number;
}

interface SelectedTopping {
  topping_id: number;
  quantity: number;
}

function PizzaList() {
  const navigate = useNavigate();
  const [pizzas, setPizzas] = useState<Pizza[]>([]);
  const [toppings, setToppings] = useState<Topping[]>([]);
  const [selectedPizza, setSelectedPizza] = useState<Pizza | null>(null);
  const [selectedToppings, setSelectedToppings] = useState<SelectedTopping[]>([]);
  const [showToppingModal, setShowToppingModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPizzas = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:8000/api/pizzas', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch pizzas');
        }

        const data = await response.json();
        setPizzas(data.data);
      } catch (err) {
        console.error('Error fetching pizzas:', err);
        setError('Failed to load pizzas');
      } finally {
        setLoading(false);
      }
    };

    const fetchToppings = async () => {
      try {
        const token = localStorage.getItem('access_token');
        const response = await fetch('http://localhost:8000/api/toppings', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch toppings');
        }

        const data = await response.json();
        setToppings(data.data);
      } catch (err) {
        console.error('Error fetching toppings:', err);
      }
    };

    fetchPizzas();
    fetchToppings();
  }, []);

  const handleAddToCart = async (pizza: Pizza) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('Please log in to add items to cart');
        return;
      }

      const selectedToppingsForPizza = selectedToppings.filter(t => t.quantity > 0);
      
      const response = await fetch('http://localhost:8000/api/cart/items', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pizza_id: pizza.id,
          quantity: 1,
          toppings: selectedToppingsForPizza,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to add item to cart');
      }

      setShowToppingModal(false);
      setSelectedToppings([]);
      navigate('/cart'); // Redirect to cart after successful addition
    } catch (err) {
      console.error('Error adding to cart:', err);
      setError('Failed to add item to cart');
    }
  };

  const handleToppingChange = (toppingId: number, quantity: number) => {
    setSelectedToppings(prev => {
      const existing = prev.find(t => t.topping_id === toppingId);
      if (existing) {
        return prev.map(t => 
          t.topping_id === toppingId ? { ...t, quantity: Math.max(0, quantity) } : t
        );
      }
      return [...prev, { topping_id: toppingId, quantity: Math.max(0, quantity) }];
    });
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  if (error) {
    return <div className="text-red-600 text-center p-4">{error}</div>;
  }

  return (
    <div>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {pizzas.map((pizza) => (
          <div key={pizza.id} className="bg-white rounded-lg shadow-md overflow-hidden">
            <img
              src={`http://localhost:8000${pizza.image}`}
              alt={pizza.name}
              className="w-full h-48 object-cover"
            />
            <div className="p-4">
              <h3 className="text-xl font-bold">{pizza.name}</h3>
              <p className="text-gray-600 mt-2">{pizza.description}</p>
              <div className="mt-4 flex justify-between items-center">
                <span className="text-xl font-bold text-red-600">₹{pizza.price.toFixed(2)}</span>
                <button
                  onClick={() => {
                    setSelectedPizza(pizza);
                    setShowToppingModal(true);
                  }}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 flex items-center space-x-1"
                >
                  <Plus size={20} />
                  <span>Add to Cart</span>
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Toppings Modal */}
      {showToppingModal && selectedPizza && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-md">
            <h2 className="text-xl font-bold mb-4">Add Toppings for {selectedPizza.name}</h2>
            <div className="space-y-3 max-h-60 overflow-y-auto">
              {toppings.map((topping) => (
                <div key={topping.id} className="flex items-center justify-between">
                  <div>
                    <span className="font-medium">{topping.name}</span>
                    <span className="text-sm text-gray-600 ml-2">₹{topping.price.toFixed(2)}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleToppingChange(
                        topping.id,
                        (selectedToppings.find(t => t.topping_id === topping.id)?.quantity || 0) - 1
                      )}
                      className="w-8 h-8 flex items-center justify-center bg-gray-100 rounded-full hover:bg-gray-200"
                    >
                      -
                    </button>
                    <span className="w-8 text-center">
                      {selectedToppings.find(t => t.topping_id === topping.id)?.quantity || 0}
                    </span>
                    <button
                      onClick={() => handleToppingChange(
                        topping.id,
                        (selectedToppings.find(t => t.topping_id === topping.id)?.quantity || 0) + 1
                      )}
                      className="w-8 h-8 flex items-center justify-center bg-gray-100 rounded-full hover:bg-gray-200"
                    >
                      +
                    </button>
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => {
                  setShowToppingModal(false);
                  setSelectedToppings([]);
                }}
                className="px-4 py-2 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                Cancel
              </button>
              <button
                onClick={() => handleAddToCart(selectedPizza)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Add to Cart
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default PizzaList;