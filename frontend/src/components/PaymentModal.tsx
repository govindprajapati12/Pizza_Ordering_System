import React, { useState } from 'react';
import { CreditCard, X } from 'lucide-react';

interface PaymentModalProps {
  amount: number;
  onClose: () => void;
  onSuccess: () => void;
  onError: (message: string) => void;
}

function PaymentModal({ amount, onClose, onSuccess, onError }: PaymentModalProps) {
  const [cardNumber, setCardNumber] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');
  const [processing, setProcessing] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setProcessing(true);

    try {
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // For testing: Succeed if card number ends with even number, fail if odd
      const lastDigit = parseInt(cardNumber.slice(-1));
      
      if (isNaN(lastDigit) || lastDigit % 2 !== 0) {
        throw new Error('Payment failed. Please try again.');
      }

      onSuccess();
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Payment failed');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-gray-500 hover:text-gray-700"
        >
          <X size={24} />
        </button>

        <div className="flex items-center space-x-2 mb-6">
          <CreditCard className="text-red-600" size={24} />
          <h2 className="text-xl font-bold">Payment Details</h2>
        </div>

        <div className="mb-4">
          <p className="text-lg font-semibold text-gray-800">
            Total Amount: ₹{amount.toFixed(2)}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Card Number
            </label>
            <input
              type="text"
              value={cardNumber}
              onChange={(e) => setCardNumber(e.target.value.replace(/\D/g, '').slice(0, 16))}
              className="w-full border rounded-md px-3 py-2"
              placeholder="1234 5678 9012 3456"
              pattern="\d{16}"
              required
              disabled={processing}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Expiry Date
              </label>
              <input
                type="text"
                value={expiryDate}
                onChange={(e) => {
                  const value = e.target.value.replace(/\D/g, '');
                  if (value.length <= 4) {
                    const month = value.slice(0, 2);
                    const year = value.slice(2);
                    setExpiryDate(value.length > 2 ? `${month}/${year}` : value);
                  }
                }}
                className="w-full border rounded-md px-3 py-2"
                placeholder="MM/YY"
                pattern="\d{2}/\d{2}"
                required
                disabled={processing}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                CVV
              </label>
              <input
                type="text"
                value={cvv}
                onChange={(e) => setCvv(e.target.value.replace(/\D/g, '').slice(0, 3))}
                className="w-full border rounded-md px-3 py-2"
                placeholder="123"
                pattern="\d{3}"
                required
                disabled={processing}
              />
            </div>
          </div>

          <button
            type="submit"
            className={`w-full bg-red-600 text-white py-3 rounded-lg font-semibold
              ${processing ? 'opacity-75 cursor-not-allowed' : 'hover:bg-red-700'}`}
            disabled={processing}
          >
            {processing ? (
              <div className="flex items-center justify-center space-x-2">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                <span>Processing...</span>
              </div>
            ) : (
              'Pay Now'
            )}
          </button>
        </form>

        <div className="mt-4 text-sm text-gray-600">
          <p className="text-center">
            Test Card: Use any 16-digit number ending with an even number for success,
            odd number for failure
          </p>
        </div>
      </div>
    </div>
  );
}


export default PaymentModal;