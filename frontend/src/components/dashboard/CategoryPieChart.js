// File: src/components/dashboard/CategoryPieChart.js
import React from 'react';
import { Pie } from 'react-chartjs-2';
import { Chart, ArcElement, Tooltip, Legend } from 'chart.js';

Chart.register(ArcElement, Tooltip, Legend);

const CategoryPieChart = ({ invoices }) => {
  const categoryCounts = invoices.reduce((acc, invoice) => {
    const rawCategory = invoice.category || "Uncategorized";

    // 🧼 Normalize: Capitalize first letter, lowercase the rest
    const category =
      rawCategory.charAt(0).toUpperCase() + rawCategory.slice(1).toLowerCase();

    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  const data = {
    labels: Object.keys(categoryCounts),
    datasets: [
      {
        label: '# of Invoices',
        data: Object.values(categoryCounts),
        backgroundColor: [
          '#1976d2', '#dc004e', '#388e3c', '#f57c00', '#9c27b0', '#009688',
        ],
        borderWidth: 1,
      },
    ],
  };

  return <Pie data={data} />;
};

export default CategoryPieChart;
