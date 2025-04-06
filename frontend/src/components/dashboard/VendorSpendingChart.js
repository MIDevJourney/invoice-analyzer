import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

// Utility to group and sum spending by vendor
const getVendorSpendData = (invoices) => {
  const grouped = {};

  invoices.forEach((inv) => {
    const vendor = (inv.vendor || 'Unknown').trim();

    if (!grouped[vendor]) {
      grouped[vendor] = 0;
    }
    grouped[vendor] += Number(inv.amount) || 0;
  });

  return Object.entries(grouped).map(([vendor, total]) => ({
    vendor,
    total: parseFloat(total.toFixed(2)),
  }));
};

const VendorSpendingChart = ({ invoices }) => {
  const data = getVendorSpendData(invoices);

  return (
    <div style={{ width: '100%', height: 300, marginBottom: '2rem' }}>
      <h3 style={{ textAlign: 'center' }}>🏢 Spending by Vendor</h3>
      <ResponsiveContainer>
        <BarChart data={data} layout="vertical" margin={{ left: 40 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis dataKey="vendor" type="category" />
          <Tooltip formatter={(value) => `$${value}`} />
          <Bar dataKey="total" fill="#388e3c" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default VendorSpendingChart;
