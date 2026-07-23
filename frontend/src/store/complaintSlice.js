import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const extractFromText = createAsyncThunk(
  "complaint/extractFromText",
  async (rawText) => {
    const res = await fetch(`${API_BASE}/api/complaints/extract`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ raw_text: rawText }),
    });
    if (!res.ok) throw new Error("Extraction failed");
    return { ...(await res.json()), rawText };
  }
);

export const extractFromFile = createAsyncThunk(
  "complaint/extractFromFile",
  async (file) => {
    const formData = new FormData();
    formData.append("file", file);
    const res = await fetch(`${API_BASE}/api/complaints/extract-file`, {
      method: "POST",
      body: formData,
    });
    if (!res.ok) throw new Error("Extraction failed");
    return await res.json();
  }
);

export const saveComplaint = createAsyncThunk(
  "complaint/saveComplaint",
  async (_, { getState }) => {
    const { complaint } = getState();
    const payload = {
      ...complaint.fields,
      raw_source_text: complaint.rawText,
      ai_extraction_confidence: complaint.aiExtractionConfidence,
      missing_fields: complaint.missingFields,
      risk_classification: complaint.riskClassification,
      capa_recommendation: complaint.capaRecommendation,
      ai_summary: complaint.aiSummary,
    };
    const res = await fetch(`${API_BASE}/api/complaints`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error("Save failed");
    return await res.json();
  }
);

const emptyFields = {
  complaint_source: "",
  customer_name: "",
  product_name: "",
  product_strength_grade: "",
  batch_lot_number: "",
  manufacturing_date: "",
  expiry_date: "",
  quantity_affected: "",
  complaint_type: "",
  complaint_date: "",
  detailed_description: "",
  initial_severity: "",
  priority: "",
};

const complaintSlice = createSlice({
  name: "complaint",
  initialState: {
    fields: emptyFields,
    rawText: "",
    missingFields: [],
    aiExtractionConfidence: null,
    riskClassification: null,
    aiSummary: null,
    capaRecommendation: null,
    possibleDuplicateId: null,
    extractionStatus: "idle", // idle | loading | succeeded | failed
    extractionProgress: 0,
    saveStatus: "idle",
  },
  reducers: {
    updateField(state, action) {
      const { name, value } = action.payload;
      state.fields[name] = value;
    },
    resetForm(state) {
      state.fields = emptyFields;
      state.rawText = "";
      state.missingFields = [];
      state.aiExtractionConfidence = null;
      state.riskClassification = null;
      state.aiSummary = null;
      state.capaRecommendation = null;
      state.possibleDuplicateId = null;
      state.extractionStatus = "idle";
    },
    setExtractionProgress(state, action) {
      state.extractionProgress = action.payload;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(extractFromText.pending, (state) => {
        state.extractionStatus = "loading";
      })
      .addCase(extractFromText.fulfilled, (state, action) => {
        state.extractionStatus = "succeeded";
        state.fields = { ...state.fields, ...action.payload.fields };
        state.rawText = action.payload.rawText;
        state.missingFields = action.payload.missing_fields;
        state.aiExtractionConfidence = action.payload.ai_extraction_confidence;
        state.riskClassification = action.payload.risk_classification;
        state.aiSummary = action.payload.ai_summary;
        state.capaRecommendation = action.payload.capa_recommendation;
        state.possibleDuplicateId = action.payload.possible_duplicate_id;
      })
      .addCase(extractFromText.rejected, (state) => {
        state.extractionStatus = "failed";
      })
      .addCase(saveComplaint.pending, (state) => {
        state.saveStatus = "loading";
      })
      .addCase(saveComplaint.fulfilled, (state) => {
        state.saveStatus = "succeeded";
      })
      .addCase(saveComplaint.rejected, (state) => {
        state.saveStatus = "failed";
      });
  },
});

export const { updateField, resetForm, setExtractionProgress } = complaintSlice.actions;
export default complaintSlice.reducer;
