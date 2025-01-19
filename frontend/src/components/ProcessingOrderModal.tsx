import React from 'react';
import { Pizza } from 'lucide-react';

function ProcessingOrderModal() {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 max-w-md w-full">
        <div className="text-center">
          <div className="animate-spin mb-4">
            <Pizza size={48} className="mx-auto text-red-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Processing Your Order</h3>
          <p className="text-sm text-gray-500">
            Please wait while we finalize your delicious pizza order...
          </p>
        </div>
      </div>
    </div>
  );
}

export default ProcessingOrderModal;