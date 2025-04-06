// File: frontend/src/components/dashboard/MonthlySpendingChart.js

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Typography, Box } from '@mui/material';
import dayjs from 'dayjs';

const MonthlySpendingChart = ({ invoices }) => {
  // Group invoices by month and sum amounts
  const monthlyTotals = invoices.reduce((acc, invoice) => {
    if (!invoice.invoice_date || !invoice.amount) return acc;
    const month = dayjs(invoice.invoice_date).format('YYYY-MM');
    acc[month] = (acc[month] || 0) + parseFloat(invoice.amount);
    return acc;
  }, {});

  // Convert into array of objects sorted by month
  const chartData = Object.entries(monthlyTotals)
    .map(([month, total]) => ({ month, total }))
    .sort((a, b) => new Date(a.month) - new Date(b.month));

  return (
    <Box sx={{ width: '100%', height: 400, mt: 5 }}>
      <Typography variant="h5" align="center" gutterBottom>
        Monthly Spending
      </Typography>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="total" stroke="#1976d2" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default MonthlySpendingChart;
