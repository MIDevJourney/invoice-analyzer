// File: src/pages/DashboardPage.js
import CategoryPieChart from '../components/dashboard/CategoryPieChart';
import MonthlySpendingChart from '../components/dashboard/MonthlySpendingChart';
import VendorSpendingChart from '../components/dashboard/VendorSpendingChart';

import InvoiceUpload from '../components/invoices/InvoiceUpload';

import { Box } from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import IconButton from '@mui/material/IconButton';
import { Divider } from '@mui/material';
import React, { useEffect, useState } from 'react';
import { getInvoices, deleteInvoice } from '../services/api';
import {
  Container,
  Typography,
  Grid,
  Paper,
  CircularProgress,
} from '@mui/material';

const DashboardPage = () => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);

  const handleDelete = async (id) => {
    try {
      await deleteInvoice(id);
      setInvoices((prev) => prev.filter((inv) => inv.id !== id));
    } catch (err) {
      console.error('Failed to delete invoice:', err);
    }
  };

  const loadInvoices = async () => {
    try {
      const data = await getInvoices();
      setInvoices(data);
    } catch (error) {
      console.error('Failed to load invoices:', error);
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    loadInvoices();
  }, []);

  if (loading) {
    return (
      <Container sx={{ mt: 4 }}>
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>Dashboard</Typography>
        <Divider sx={{ mb: 2 }} />

        {/* 🆕 Upload Component */}
        <InvoiceUpload onUploadSuccess={loadInvoices} />

        <Divider sx={{ mt: 4, mb: 4 }} />


      {invoices.length === 0 ? (
        <Typography>No invoices uploaded yet.</Typography>
      ) : (
        <>
          {/* SUMMARY CARDS - LEFT ALIGNED */}
          <Grid container spacing={2} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={4}>
              <Paper sx={{ p: 2, minWidth: 200, textAlign: 'center', boxShadow: 3 }}>
                <Typography variant="h6">Total Invoices</Typography>
                <Typography variant="h4">{invoices.length}</Typography>
              </Paper>
            </Grid>
            <Grid item xs={12} sm={6} md={4}>
              <Paper sx={{ p: 2, minWidth: 200, textAlign: 'center', boxShadow: 3 }}>
                <Typography variant="h6">Total Spend</Typography>
                <Typography variant="h4">
                ${invoices.reduce((sum, inv) => sum + (Number(inv.amount) || 0), 0).toFixed(2)}
                </Typography>
              </Paper>
            </Grid>
          </Grid>

          {/* CATEGORY CHART */}
          <Box sx={{ maxWidth: 400, mb: 4 }}>
            <Typography variant="h5" gutterBottom align="center">
              Invoice Categories
            </Typography>
            
            
            <Box sx={{ mb: 5 }}>
            <CategoryPieChart invoices={invoices} />
</Box>


            <Box sx={{ mb: 5 }}>
  <MonthlySpendingChart invoices={invoices} />
</Box>

<Box sx={{ mb: 5 }}>
  <VendorSpendingChart invoices={invoices} />
</Box>
          </Box>

          {/* INVOICE LIST */}
          <Grid container spacing={2} sx={{ mt: 4 }}>
            {invoices.map((invoice) => (
              <Grid item xs={12} sm={6} md={4} key={invoice.id}>
                <Paper
                  sx={{
                    p: 2,
                    position: 'relative',
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                >
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                    <Typography variant="h6" sx={{ fontWeight: 'bold' }}>{invoice.vendor}</Typography>
                    <IconButton
                      onClick={() => handleDelete(invoice.id)}
                      sx={{ color: 'error.main' }}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                  <Typography>
  ${invoice.amount != null ? Number(invoice.amount).toFixed(2) : 'N/A'}
</Typography>

                  <Typography>Date: {invoice.invoice_date}</Typography>
                  <Typography>
  Category:{' '}
  {invoice.category
    ? invoice.category.charAt(0).toUpperCase() + invoice.category.slice(1).toLowerCase()
    : 'Uncategorized'}
</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </>
      )}
    </Container>
  );
};

export default DashboardPage;
