// File: frontend/src/components/invoices/InvoiceUpload.js

import React, { useState, useRef } from "react";
import {
  Box,
  Button,
  Typography,
  CircularProgress,
  TextField,
  Paper,
} from "@mui/material";
import axios from "axios";

const InvoiceUpload = ({ onUploadSuccess }) => {
    const [manualEntry, setManualEntry] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [metadata, setMetadata] = useState({
    vendor: "",
    amount: "",
    invoice_date: "",
    category: "",
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const fileInputRef = useRef();

  const handleFileDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
    } else {
      setMessage("Only PDF files allowed");
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file && file.type === "application/pdf") {
      setSelectedFile(file);
    } else {
      setMessage("Only PDF files allowed");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile && !manualEntry) {
        setMessage("Please select a PDF invoice or enable manual entry.");
        return;
      }
      

    const formData = new FormData();
    formData.append("file", selectedFile);

    // 🧼 Clean metadata: handle empty amount properly
    const safeMetadata = {
      ...metadata,
      amount: metadata.amount === "" ? null : parseFloat(metadata.amount),
    };

    formData.append("invoice_data", JSON.stringify(safeMetadata));

    try {
      setLoading(true);
      setMessage("");

      const token = localStorage.getItem("token");
      console.log("Token being used for upload:", token);

      const response = await axios.post("http://localhost:8000/invoices/", formData, {
        headers: {
          "Authorization": `Bearer ${token}`,
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.status === 201 || response.status === 200) {
        setMessage("✅ Upload successful!");
        setSelectedFile(null);
        setMetadata({ vendor: "", amount: "", invoice_date: "", category: "" });
        if (onUploadSuccess) onUploadSuccess();
      } else {
        setMessage("❌ Upload failed. Check the server.");
      }
    } catch (error) {
      setMessage("❌ Error uploading file.");
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper
      elevation={3}
      onDrop={(e) => !manualEntry && handleFileDrop(e)}
  onDragOver={(e) => !manualEntry && e.preventDefault()}
      sx={{
        p: 3,
        mt: 3,
        border: "2px dashed #aaa",
        borderRadius: "12px",
        textAlign: "center",
        backgroundColor: "#fafafa",
      }}
    >
      <Typography variant="h6">Upload Invoice (PDF only)</Typography>
      {!manualEntry && (
  <Box mt={2}>
    <input
      ref={fileInputRef}
      type="file"
      hidden
      onChange={handleFileSelect}
    />
    <Button onClick={() => fileInputRef.current.click()} variant="outlined">
      Select File
    </Button>
    <Typography variant="body2" mt={1}>
      Or drag & drop a PDF here
    </Typography>
    {selectedFile && (
      <Typography mt={1}>Selected File: {selectedFile.name}</Typography>
    )}
  </Box>
)}

      <Box mt={3}>
        <TextField
          fullWidth
          label="Vendor"
          value={metadata.vendor}
          onChange={(e) => setMetadata({ ...metadata, vendor: e.target.value })}
          margin="normal"
        />
        <TextField
          fullWidth
          label="Amount"
          type="number"
          value={metadata.amount}
          onChange={(e) =>
            setMetadata({ ...metadata, amount: e.target.value })
          }
          margin="normal"
        />
        <TextField
          fullWidth
          label="Invoice Date"
          type="date"
          value={metadata.invoice_date}
          onChange={(e) =>
            setMetadata({ ...metadata, invoice_date: e.target.value })
          }
          margin="normal"
          InputLabelProps={{ shrink: true }}
        />
        <TextField
          fullWidth
          label="Category"
          value={metadata.category}
          onChange={(e) => setMetadata({ ...metadata, category: e.target.value })}
          margin="normal"
        />
      </Box>
        <Box mt={2}>
        <label>
            <input
            type="checkbox"
            checked={manualEntry}
            onChange={() => setManualEntry(!manualEntry)}
            />
            &nbsp;I want to enter this invoice manually (no PDF upload)
        </label>
        </Box>


      <Box mt={2}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleUpload}
          disabled={loading}
        >
          {loading ? <CircularProgress size={24} /> : "Upload Invoice"}
        </Button>
      </Box>

      {message && (
        <Typography mt={2} color="error">
          {message}
        </Typography>
      )}
    </Paper>
  );
};

export default InvoiceUpload;
